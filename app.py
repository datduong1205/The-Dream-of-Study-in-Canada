"""An editorial data story. Run with: python -m streamlit run app.py."""

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
STATCAN = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3710004501"
IRCC = "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/study-permit/get-documents/financial-support.html"
WATERLOO = "https://uwaterloo.ca/future-graduate-students/funding/living-costs-and-housing"
CONTENT_WIDTH = 1080
BUDGET_DEFAULTS = {
    "housing": 950,
    "groceries": 380,
    "transportation": 175,
    "phone": 50,
    "hours": 20,
    "wage": 20,
}
REFERENCE = {
    "Housing and utilities": 950,
    "Groceries": 385,
    "Phone": 106,
    "Entertainment": 150,
    "Personal care": 80,
    "Clothing": 132,
    "Laundry": 43,
    "Transportation": 28,
    "Books and supplies": 247,
}
# Explicit category keys keep chart and table colours stable if rows are reordered.
CATEGORY_COLORS = {
    "Housing and utilities": "#1c83e1",
    "Groceries": "#84cc16",
    "Phone": "#f43f5e",
    "Entertainment": "#f59e0b",
    "Personal care": "#10b981",
    "Clothing": "#8b5cf6",
    "Laundry": "#2dd4bf",
    "Transportation": "#f97316",
    "Books and supplies": "#79b9f0",
}


def prose(text, *, allow_html=False):
    """Escape dollar signs so adjacent prices never become inline LaTeX."""
    st.markdown(text.replace("$", r"\$"), unsafe_allow_html=allow_html)


def reference_budget_figure():
    """Pair the composition graphic with an exact, accessible category summary."""
    with st.container(key="figure_reference_budget"):
        chart, summary = st.columns([1, 1.15], gap="large", vertical_alignment="center")
        with chart:
            with st.container(key="reference_donut"):
                st.image(str(ROOT / "donut_chart.png"), width="stretch")
        with summary:
            rows = "".join(
                f'<tr><th scope="row"><span class="expense-swatch" '
                f'style="background-color:{CATEGORY_COLORS[name]}" aria-hidden="true"></span>'
                f'{escape(name)}</th><td>${value:,.0f}</td></tr>'
                for name, value in REFERENCE.items()
            )
            st.html(
                '<div class="expense-panel"><table class="expense-summary">'
                '<caption>Reference student budget · CAD per month</caption>'
                '<thead><tr><th scope="col">Category</th><th scope="col">Monthly cost</th></tr></thead>'
                f'<tbody>{rows}</tbody><tfoot><tr><th scope="row">Total</th>'
                f'<td>${sum(REFERENCE.values()):,.0f}</td></tr></tfoot></table></div>'
            )
        st.caption(f"Source: [University of Waterloo, living costs and housing]({WATERLOO}). Created using Tableau Desktop")


@st.cache_data
def load_tuition():
    """Read only the source tables used by the page's tuition explanations."""
    domestic = pd.read_csv(ROOT / "Canadian_student.csv").set_index("Year")
    international = pd.read_csv(ROOT / "International_student.csv").set_index("Year")
    graduate = pd.read_csv(ROOT / "graduate_tuition_region.csv").set_index("Region")
    if not domestic.index.equals(international.index):
        raise ValueError("Domestic and international tuition years do not align.")
    return domestic, international, graduate


def tableau(filename):
    with st.container(key=f"figure_{Path(filename).stem}"):
        st.image(str(ROOT / filename), width="stretch")
        st.caption(
            f"Source: [Statistics Canada, tuition fees for degree programs]({STATCAN}). "
            "Created using Tableau Desktop"
        )


def budget_totals(housing, groceries, transportation, phone, hours, wage):
    """Convert weekly gross pay to a monthly average, without rounding intermediate values."""
    expenses = housing + groceries + transportation + phone
    earnings = hours * wage * 52 / 12
    return expenses, earnings, earnings - expenses


def budget_slider(label, name, minimum, maximum, step, unit="currency"):
    value = st.session_state[f"budget_{name}"]
    display = f"${value:,.0f}" if unit == "currency" else f"{value} h"
    st.html(
        f'<div class="budget-control-label"><span>{escape(label)}</span>'
        f'<span>{display}</span></div>'
    )
    return st.slider(
        label,
        min_value=minimum,
        max_value=maximum,
        step=step,
        key=f"budget_{name}",
        label_visibility="collapsed",
    )


@st.fragment
def budget_calculator():
    for name, value in BUDGET_DEFAULTS.items():
        st.session_state.setdefault(f"budget_{name}", value)
    with st.container(border=True, key="budget_calculator"):
        st.subheader("Build Calculator")
        left, right = st.columns(2, gap="large")
        with left:
            housing = budget_slider("Housing & utilities", "housing", 400, 3000, 25)
            transportation = budget_slider("Transportation", "transportation", 0, 300, 5)
        with right:
            groceries = budget_slider("Groceries", "groceries", 150, 700, 5)
            phone = budget_slider("Phone bills", "phone", 0, 200, 1)
        hours = budget_slider(
            "Part-time work (hours/week)", "hours", 0, 24, 1, unit="hours"
        )
        wage = budget_slider("Hourly wage (CAD)", "wage", 0, 50, 1)
        expenses, earnings, balance = budget_totals(
            housing, groceries, transportation, phone, hours, wage
        )
        if balance > 0:
            status = "surplus"
        elif balance < 0:
            status = "shortfall"
        else:
            status = "balanced"
        sign = "+" if balance > 0 else "−" if balance < 0 else ""
        signed_balance = f"{sign}${abs(balance):,.2f}"
        st.html(
            '<section class="budget-results" aria-label="Monthly budget results" aria-live="polite">'
            f'<div class="budget-result-row"><span>Monthly expenses</span><strong>${expenses:,.2f}</strong></div>'
            f'<div class="budget-result-row"><span>Estimated gross earnings</span><strong>${earnings:,.2f}</strong></div>'
            '<div class="budget-balance-row"><strong>Monthly balance</strong>'
            f'<strong class="budget-balance {status}">{signed_balance}</strong></div>'
        )

def main():
    st.set_page_config(
        page_title="Dat Duong",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.html(f"<style>{(ROOT / 'style.css').read_text(encoding='utf-8')}</style>")
    try:
        # Retain source-file validation even though narrative figures are authored text.
        load_tuition()
    except (OSError, ValueError, KeyError) as error:
        st.error(f"The original tuition CSV files could not be loaded: {error}")
        st.stop()

    with st.container(key="story", horizontal_alignment="center"):
        with st.container(width=CONTENT_WIDTH):
            st.title("The Dream of Study in Canada")
            st.header("Part I: The Opportunity")
            prose("For as long as she can remember, An has dreamed of studying abroad. Growing up in Vietnam, she imagined what it would be like to experience a new country. "
                  "Meet people from different background and pursue an education overseas")
            prose("Now, at 22, that dream has become a reality. An is pursuing her master's degree at the University of Waterloo in Ontario. She rents a room in a shared house and work part-time while balancing her classes, assignment, and everyday responsibilites. ")
            prose("Moving to Canada has opened the door to new opportunities, but it als brought financial challenges she hadn't fully understood before arriving. Beyond tuition, An must think about rent, groceries, transportation, and all the smaller expenses that come with living independently. "
                  "Through An's journey, we'll explore what it really costs to study in Canada and the financial decisions that international student like her face along the way.")
            st.image(str(ROOT / "nathan_philips.jpg"), width="stretch")
            st.header("Part II: The Price of Education")
            prose("Before coming to Canada, An knew studying abroad would be expensive. Tuition was one of "
                  "the first things she and her family had to consider. She expected international students to pay more "
                  "than domestic students, but **how much more ?**")

        with st.container(width=CONTENT_WIDTH, key="tuition_figure"):
            tableau("tuition_trend.png")
        with st.container(width=CONTENT_WIDTH):
            prose('In **2025/2026**, international undergraduate students paid an average of '
                  '<span class="tuition-international-undergraduate">$41,746</span> per year, '
                  'while domestic students paid <span class="tuition-domestic-undergraduate">$7,734</span> on average. '
                  "That's about 5.4 times as much. The undergraduate gap has also widened over the decade, with international undergraduate tuition rising considerably faster. ",
                  allow_html=True)
            prose("For An, who is pursuing a master's degree, the graduate figures are more relevant. "
                  "International graduate students paid an average of "
                  '<span class="tuition-international-graduate">$24,028</span> compared to '
                  '<span class="tuition-domestic-graduate">$7,978</span> for domestic students. '
                  "Although the exact fees would vary depend on program and university but these figures would suggest her the range she need to commit to. ",
                  allow_html=True)
            prose("However, An soon discover that where she chooses to study and live also matter as much.")
            st.subheader("Where You Study Also Matters")
            prose("When An choosing a university, she focused on finding a program that matched her interest and future career goals. "
                  "The University of Waterloo offered her the program she was looking for at one of the top ranking university in Canada."
                  "But studying in Ontario also meant that she will have to manage her budget more tightly. ")
            prose("tuition fees can vary considerably depending on the province. The maps below compare average graduate tuition for domestic and international students across ten Canadian provinces in **2025/2026**."
                  "Switch between the two tab to see how the costs change. ")
            prose("Ontario, where An studies, had the highest average international graduate tuition at **$28,624**, while Newfoundland and Labrador had the lowest at **$6,964**. That's more than four times the amount.")
            prose("**Why such a large difference?** "
                  "In Canada, provincianl government play an important role in funding universities and regulating tuition. Each province has its own education policies while tuition also differ in universities, their programs and funding recieved.")
            prose("Canada's immigration policies also an important reason. As the federal government has introduced limits on international study permits and distributes application allocations across provinces and territories, partly in response to pressures on housing and public services. "
                  "This means institutions that rely heavily on international students will be short on their revenue. ")
        with st.container(width=CONTENT_WIDTH):
            group = st.segmented_control("Compare graduate tuition", ["Domestic", "International"],
                                         default="Domestic", key="map_group")
            tableau("domestic_tuition_map.png" if group == "Domestic" else "international_tuition_map.png")

            prose("Ontario has the highest average international graduate tuition among these ten "
                  "provinces at **$28,624**, while Newfoundland and Labrador has the lowest at **$6,964**. "
                  "That is more than four times as much. These are provincial averages rather than "
                  "individual program fees, so An still needs to check the costs of her own degree.")
            prose("The comparison adds a financial dimension to her choice of university. A program's "
                  "location matters alongside its academic opportunities—and tuition is only the beginning. "
                  "Once she arrives in Waterloo, another set of expenses becomes part of everyday life.")

            st.header("Part III: Beyond Tuition")
            prose("After arriving in Waterloo, An begins settling into her new routine. Between attending lectures, completing assignment, and working part-time, she also has to manage the responsibilies when living alone. "
                  "Every month, there is rent to pay, groceries to buy, and several other fees such as transportation, entertainment, or insurance.")
            prose("Before coming to Canada, An also had to demonstrate that she had the sufficient funds to support herself while studying. But how much money does the Canadian goverment expect she to have? ")
            st.subheader("Initial Financial Requirement")
            st.html(
                '<section class="ircc-stat" aria-label="Proof of Financial Support">'
                '<div class="ircc-stat-context">Proof of Financial Support</div>'
                '<div class="ircc-stat-number">$1,954</div>'
                '<div class="ircc-stat-unit">CAD per month</div>'
                '<div class="ircc-stat-details">Annual requirement: $23,448 · '
                'Outside of Quebec</div>'
                '</section>'
            )
            st.caption(f"Source: [IRCC, proof of financial support]({IRCC})")
            prose("")
            prose("As required by the IRCC, An must demonstrate"
                  " **$23,448** in living-expense funds for one year, "
                  "equivalent to **$1,954 per month**. However, this amount is an immigration financial requirement, not a fixed monthly spending budget. "
                  "For someone like An, who has to manage expenses while keeping up with universtiy, let's look into how much she might actually need each month.")
            st.subheader("Estimated Monthly Living Expenses")
            prose("Sharing a house means An does not live alone, but rent is still only one part of "
                  "the budget she needs to think about. Waterloo's published living-cost estimates offer a "
                  "useful reference for a single student in the city. They provide a useful example of what a student "
                  "living in Waterloo might need to budget each month.")
            prose("An pays **$950** monthly for housing and utilities (the lower end of the university's housing range), "
                  "the total comes to **$2,121 per month**. It includes groceries, transportation, "
                  "phone costs, books and other personal expenses. ")
            prose("The donut chart below shows how these expenses are distributed. "
                  "Housing takes up the largest part of An's budget, but the smaller categories also add up very quickly. "
                  "These are basic necessities that An have to pay to maintain a normal and functional everyday life and it can make a noticeable difference.")
            reference_budget_figure()
            prose("This reference budget is **$167 above** the what IRCC required An to demonstrate in the first place. "
                  "The two figures serve different purposes, so this doesn't necessarily mean the government's requirement is insufficient. "
                  "However, it does show why relying on a single estimate may not tell the whole story."
                  " An's actual spending could be higher or lower depending on her rent and spending habits. "
                  "She can make choices about some expenses, but still needs to meet "
                  "basic living costs.")

            st.header("Part IV: A Closer Look at An's Budget ")

            budget_calculator()

            prose("At first glance, An's budget may seem manageable. With monthly expenses of **$1,555** and estimated earnings of **$1,646**, there is a small surplus of around $91."
                  "But that leaves very little room for unexpected expenses and savings. A higher grocery bill, an increase in rent, or even a few missed work shifts could quickly turn that surplus into a shortfall. "
                  "And with 20 hours of work each week, An must also consider how much time remains for studying and other responsibilities. ")
            prose("This has shown one of the challenges that every international students not just An face in Canada. Balancing a budget is not just about earning enough to pay the bills. "
                  "It is also about making financial decisions that allow students to focus on the educationt that they came here to pursue.")

if __name__ == "__main__":
    main()
