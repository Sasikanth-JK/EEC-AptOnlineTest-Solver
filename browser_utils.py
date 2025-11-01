from playwright.async_api import async_playwright, Playwright, Browser, Page
from logger import LOGGER

async def create_driver() -> tuple[Playwright, Browser]:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False) # False for see the actions
    context = await browser.new_context()
    return playwright, context
    
async def stop_driver(playwright: Playwright, browser: Browser) -> None:
    await browser.close()
    await playwright.stop()
    

async def get_total_questions(page) -> int:
    total_questions = await page.evaluate("""
        () => {
            // Find all inputs with onclick starting with the function
            const buttons = Array.from(document.querySelectorAll('input[onclick]'));
            return buttons.filter(btn => btn.getAttribute('onclick').includes('JsController.apdata.action.LoadQuestionByNo')).length;
        }
    """)
    return total_questions

async def get_current_question_details(page: Page) -> dict:
    question_elems = await page.query_selector_all(
    "div[style*='margin-bottom:7px'][style*='font-weight:bold']"
)

    question = " ".join([(await div.inner_text()).strip() if div else "" for div in question_elems])
    
    options = []
    label_elements = await page.query_selector_all(".qst_ans_table .rbcontainer")
    
    for label in label_elements:
        text = (await label.inner_text()).strip()
        input_tag = await label.query_selector("input")
        if input_tag:
            value = await input_tag.get_attribute("value")
            selected = await input_tag.is_checked()
        else:
            value = None
            selected = False

        options.append({
            "text": text,
            "value": value,
            "selected": selected
        })

    return {
        "question": question,
        "options": options
    }