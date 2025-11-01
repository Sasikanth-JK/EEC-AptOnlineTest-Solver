import json
from asyncio import get_event_loop, sleep
from playwright.async_api import Page

from config import Config
from browser_utils import create_driver, stop_driver, get_current_question_details, get_total_questions
from gemini_utils import initialize_gemini, safe_gen_wrapper
from logger import LOGGER
from ext_utils import is_already_completed


async def perform_action(
    page: Page,
    action: str,
    selector_type: str,
    selector_value: str,
    text: str = None,
    timeout: int = 10000
):
    """
    Perform an action on a page element.

    Args:
        page: Playwright Page
        action: 'click' | 'fill' | 'wait'
        selector_type: 'role', 'css', 'xpath'
        selector_value: the value for selector
        text: text to fill if action is 'fill'
        timeout: wait timeout in ms
        logger: optional logger
    """
    try:
        if selector_type == "role":
            if not isinstance(selector_value, dict) or "role" not in selector_value:
                raise ValueError("For 'role' selector_type, selector_value must be a dict with at least a 'role' key")
            role = selector_value["role"]
            options = {k: v for k, v in selector_value.items() if k != "role"}
            element = page.get_by_role(role, **options)
        elif selector_type == "css":
            element = page.locator(selector_value)
        elif selector_type == "xpath":
            element = page.locator(f"xpath={selector_value}")
        else:
            raise ValueError("Invalid selector_type")

        await element.wait_for(state="visible", timeout=timeout)

        if action == "click":
            await element.click()
            LOGGER.info(f"Clicked element {selector_value}")
        elif action == "fill":
            if text is None:
                raise ValueError("Text must be provided for fill action")
            await element.fill(text)
            LOGGER.info(f"Filled element {selector_value} with text: {text}")
        elif action == "wait":
            LOGGER.info(f"Element {selector_value} is visible")
        else:
            raise ValueError("Invalid action")

    except Exception as e:
        LOGGER.error(f"Failed to perform {action} on {selector_value}: {e}")
        
        
async def solve_current_question(page: Page, model, question_details: dict, tries=0):
    LOGGER.info(f"Solving question: {question_details['question']}")
    
    if tries >= 3:
        LOGGER.error("Max retries reached for this question. Skipping...")
        await page.evaluate("JsController.apdata.action.NextQuestion();")
        return
    
    prompt = "Answer the following quiz. Return option id and explanation in JSON format.\n\n"
    prompt += f"Question: {question_details['question']}\n"
    prompt += "Options:\n"
    for opt in question_details['options']:
        prompt += f"{opt['value']}. {opt['text']}\n"
    response = await safe_gen_wrapper(model, prompt)
    if not response:
        LOGGER.error("No response from model.")
        return await solve_current_question(page, model, question_details, tries=tries+1)
    answers = json.loads(response.text)
    LOGGER.info(f"Model's answer: {answers}")
    if 'option_id' in answers:
        option_to_select = answers['option_id']
        for opt in question_details['options']:
            if opt['value'] == option_to_select:
                LOGGER.info(f"Selecting option {opt['value']}: {opt['text']}")
                # await page.locator(f"#rdAns[value='{opt['value']}']").check()
                await page.get_by_role("cell", name=opt['text'], exact=True).locator("span").click()
                await page.evaluate("JsController.apdata.action.NextQuestion();")
                break
        else:
            LOGGER.warning(f"Option {option_to_select} not found among available options.")
    await sleep(5)
    
    
async def change_question(page: Page, q_no: int):
    await page.evaluate(f"JsController.apdata.action.LoadQuestionByNo({q_no});")


async def finish_test(page: Page, state=""):
    
    if len(state) == 0:
        try:
            finish_link = page.get_by_role("link", name="Finish ✔")
            await finish_link.wait_for(state="visible", timeout=3000)
            await finish_link.click()
            LOGGER.info(f"Clicked Finish link")
            await sleep(1)
            return await finish_test(page, state="final")
        except Exception:
            LOGGER.info(f"Finish link not found/needed")
    
    try:
        finish_button = page.get_by_role("button", name="Finish")
        await finish_button.wait_for(state="visible", timeout=3000)
        await finish_button.click()
        LOGGER.info(f"Clicked final Finish button")
        await sleep(2)
        return True
        
    except Exception as e:
        LOGGER.warning(f"Final Finish button not found: {e}")
        return False
            
    except Exception as e:
        LOGGER.error(f"Error : {e}")
        return False
    
    
async def start_test(page: Page, model):
    if is_already_completed(await page.content()):
        LOGGER.info("Test is already completed.")
        return

    await perform_action(page, action="click", selector_type="role", selector_value={"role": "link", "name": "Start"})

    await perform_action(page, action="click", selector_type="role", selector_value={"role": "button", "name": "Continue"})

    try:
        await page.wait_for_load_state("networkidle")
    except Exception as e:
        LOGGER.warning(f"Exception while waiting for network idle: {e}")
        return

    total_questions = await get_total_questions(page)
    LOGGER.info(f"Total questions in the test: {total_questions}")
    for q_no in range(1, total_questions+1):
        question_details = await get_current_question_details(page)
        LOGGER.info(f"Question {q_no}: {question_details['question']}")
        for opt in question_details['options']:
            LOGGER.info(f" - Option {opt['value']}: {opt['text']} (Selected: {opt['selected']})")
        
        await solve_current_question(page, model, question_details)
        
        if q_no < total_questions - 1:
            await change_question(page, q_no+1)
            await page.wait_for_load_state("networkidle")
    LOGGER.info("All questions processed. Submitting the test...")
    input("Press Enter to submit the test manually...")
    await finish_test(page)



async def login(page: Page, portal_url, username: str, password: str) -> None:
    await page.goto(portal_url)
    await page.wait_for_load_state("networkidle")
    await page.get_by_role("textbox", name="User Name").wait_for(state="visible")
    await page.get_by_role("textbox", name="User Name").fill(username)
    
    await page.get_by_role("textbox", name="Password").wait_for(state="visible")
    await page.get_by_role("textbox", name="Password").fill(password)
    
    button = page.locator("#uxDoLogin")
    await button.wait_for(state="visible", timeout=10000)
    await button.click()
    
    await page.wait_for_load_state("networkidle")
    LOGGER.info("Logged in successfully.")
    
async def main():
    if not Config.GEMINI_API_KEY:
        LOGGER.error("GEMINI_API_KEY is not set in config.py")
        return
    if not any([Config.USER_ID, Config.PASSWORD]):
        LOGGER.error("USER_ID or PASSWORD is not set in config.py")
        return
    model = initialize_gemini(Config.GEMINI_API_KEY)
    playwright, browser = await create_driver()
    page = await browser.new_page()
    await login(page, Config.PORTAL_URL, Config.USER_ID, Config.PASSWORD)
    await start_test(page, model)
    LOGGER.info("Test process completed.")
    await stop_driver(playwright, browser)

if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())

    