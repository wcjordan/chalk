def get_active_work_context(page):
    active_chip = page.locator('[data-testid="work-context-filter"] [data-testid="chip-active"]')
    if not active_chip:
        return None
    return active_chip.text()


def select_work_context(page, work_context):
    work_context_chip = page.locator(f'[data-testid="work-context-filter"] :text-is("{work_context}')
    work_context_chip.click()
