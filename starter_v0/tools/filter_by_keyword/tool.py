def filter_by_keyword(items=None, keyword=""):
    try:
        if not isinstance(keyword, str) or not keyword.strip():
            raise ValueError("Từ khóa phải là văn bản không rỗng")

        if not isinstance(items, list):
            raise ValueError("items phải là một danh sách")

        results = []
        search_word = keyword.strip().casefold()

        for item in items:
            if not isinstance(item, dict):
                raise TypeError("Mỗi mục phải là một đối tượng")

            title = item.get("title", "")
            summary = item.get("summary", "")

            if not isinstance(title, str) or not isinstance(summary, str):
                raise TypeError("Tiêu đề và tóm tắt phải là văn bản")

            content = (title + " " + summary).casefold()

            if search_word in content:
                results.append(item)

        return {
            "items": results,
            "count": len(results)
        }

    except Exception as error:
        return {
            "error": type(error).__name__,
            "message": str(error)
        }