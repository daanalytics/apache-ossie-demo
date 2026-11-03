#!/usr/bin/env python3
"""Record a walkthrough of the Streamlit in Snowflake demo.

Sign in once in the browser window this script opens. The login is kept in
recording/.browser-profile, and the video is written to recording/output.
"""

import argparse
from pathlib import Path

from playwright.sync_api import Frame, Page, sync_playwright

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
PROFILE = ROOT / ".browser-profile"

TABS = [
    "What is Ossie?",
    "Ossie YAML Spec",
    "Ossie → Snowflake Mapping",
    "With vs Without",
    "The Vision",
]
YAML_SECTIONS = ["Full Model", "Sources", "Relationships", "Dimensions", "Metrics"]
QUESTIONS = [
    "Total Revenue by Region",
    "Average Order Value by Segment",
    "Active Customers Over Time",
    "Revenue by Product Category",
    "Monthly Revenue Trend",
]


def find_app_frame(page: Page) -> Frame:
    """Return the frame that actually hosts the Streamlit app."""
    for _ in range(90):
        for frame in page.frames:
            try:
                if frame.locator('[data-testid="stApp"]').count() > 0:
                    return frame
            except Exception:
                continue
        page.wait_for_timeout(1000)
    raise RuntimeError(
        "Could not find the Streamlit app. Open it in the browser window, then run again."
    )


def pause(frame: Frame, milliseconds: int) -> None:
    frame.wait_for_timeout(milliseconds)


def scroll_through(frame: Frame, pause_ms: int) -> None:
    container = frame.locator('[data-testid="stMain"]')
    if container.count() == 0:
        container = frame.locator('[data-testid="stAppViewContainer"]')
    if container.count() == 0:
        pause(frame, pause_ms)
        return

    position = 0
    scroll_height = container.evaluate("el => el.scrollHeight")
    client_height = container.evaluate("el => el.clientHeight")
    step = max(int(client_height * 0.65), 280)
    while position < scroll_height:
        container.evaluate(
            "(el, top) => el.scrollTo({top, behavior: 'smooth'})",
            position,
        )
        pause(frame, pause_ms)
        position += step
        scroll_height = container.evaluate("el => el.scrollHeight")
    container.evaluate("el => el.scrollTo({top: 0, behavior: 'smooth'})")
    pause(frame, pause_ms)


def click_name(frame: Frame, role: str, name: str) -> None:
    control = frame.get_by_role(role, name=name)
    if control.count() == 0:
        control = frame.get_by_text(name, exact=True)
    control.first.click()


def choose_question(frame: Frame, question: str, pause_ms: int) -> None:
    click_name(frame, "combobox", "Select a question:")
    pause(frame, 400)
    option = frame.get_by_role("option", name=question)
    if option.count() == 0:
        option = frame.get_by_text(question, exact=True)
    option.first.click()
    frame.get_by_text("Generated query").wait_for()
    try:
        frame.get_by_text("Expression the view applies").wait_for(timeout=45000)
    except Exception:
        pass
    try:
        frame.get_by_text("rows are selected").wait_for(timeout=45000)
    except Exception:
        pass
    pause(frame, pause_ms)
    scroll_through(frame, pause_ms)


def walk(frame: Frame, pause_ms: int) -> None:
    click_name(frame, "tab", TABS[0])
    pause(frame, pause_ms)
    scroll_through(frame, pause_ms)

    click_name(frame, "tab", TABS[1])
    pause(frame, pause_ms)
    for section in YAML_SECTIONS:
        click_name(frame, "radio", section)
        pause(frame, pause_ms)
    scroll_through(frame, pause_ms)

    click_name(frame, "tab", TABS[2])
    pause(frame, pause_ms)
    scroll_through(frame, pause_ms)

    click_name(frame, "tab", TABS[3])
    pause(frame, pause_ms)
    for question in QUESTIONS:
        choose_question(frame, question, pause_ms)

    click_name(frame, "tab", TABS[4])
    pause(frame, pause_ms)
    scroll_through(frame, pause_ms)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        required=True,
        help="Snowsight URL of the deployed Streamlit app",
    )
    parser.add_argument(
        "--pause",
        type=int,
        default=1500,
        help="Milliseconds to hold each view (default: 1500)",
    )
    args = parser.parse_args()

    OUTPUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            str(PROFILE),
            headless=False,
            viewport={"width": 1600, "height": 1000},
            record_video_dir=str(OUTPUT),
            record_video_size={"width": 1600, "height": 1000},
        )
        page = context.pages[0] if context.pages else context.new_page()
        video = page.video
        page.goto(args.url, wait_until="domcontentloaded")
        print("Sign in if Snowflake asks, and wait until the Streamlit app is on screen.")
        input("Press Enter to start recording the walkthrough... ")
        frame = find_app_frame(page)
        walk(frame, args.pause)
        pause(frame, args.pause)
        context.close()
        if video is not None:
            print(f"Saved {video.path()}")


if __name__ == "__main__":
    main()
