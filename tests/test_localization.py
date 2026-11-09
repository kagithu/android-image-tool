from android_image_tool.i18n import LANG
from android_image_tool.tooling import platform_tools_url


def test_locales_are_file_backed() -> None:
    assert LANG["ja"]["title"] == "Android イメージツール"
    assert LANG["en"]["missing_tool"]


def test_platform_tools_url_is_official() -> None:
    assert platform_tools_url().startswith("https://dl.google.com/android/repository/")
