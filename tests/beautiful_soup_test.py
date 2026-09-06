from bs4 import BeautifulSoup

html = """
<div class="card my-0 gap-3 metadata-difficulty-card">
    <span
        class="self-center whitespace-nowrap difficulty_number
               difficulty_number-problem_view difficulty_hard"
    >
        1.9 - 7.4
    </span>
</div>
<div class = "card my-0 gap-3 metadata-memory-card" >
    <i
    class = "fas fa-memory text-3xl self-center"
    style = "color: #ced5e4"
    > </i>
    <div class ="flex flex-col gap-2 self-center">
    <span class ="info_label">Memory limit</span>
    <span class ="text-lg font-bold text-link">1024 MB</span>
    </div >
</div>
"""
soup = BeautifulSoup(html, "html.parser")

element = soup.select_one("span.difficulty_number")
difficulty = element.get_text(strip=True)

print(difficulty)


element = soup.select_one(
    ".metadata-memory-card span.text-lg.font-bold.text-link"
)

memory_limit = element.get_text(strip=True) if element else None

print(memory_limit)
