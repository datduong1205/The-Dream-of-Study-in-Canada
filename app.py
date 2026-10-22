"""An editorial data story. Run with: python -m streamlit run app.py."""

from html import escape
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parent
STATCAN = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3710004501"
IRCC = "https://www.canada.ca/en/immigration-refugees-citizenship/services/study-canada/study-permit/get-documents/financial-support.html"
WATERLOO = "https://uwaterloo.ca/future-graduate-students/funding/living-costs-and-housing"
# Text, figures and controls share one editorial measure and the same left edge.
CONTENT_WIDTH = 1080
PLOT_CONFIG = {"displayModeBar": False, "scrollZoom": False}
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
# Palette roots from the Movies demo's theme; used by the expense chart and summary table.
CATEGORY_COLORS = dict(zip(REFERENCE, [
    "#1c83e1", "#84cc16", "#f43f5e", "#f59e0b", "#10b981",
    "#8b5cf6", "#2dd4bf", "#f97316", "#79b9f0",
]))
def prose(text, *, allow_html=False):
    """Escape dollar signs so adjacent prices never become inline LaTeX."""
    st.markdown(text.replace("$", r"\$"), unsafe_allow_html=allow_html)


def expense_donut(expenses):
    """Build the reference expense chart with its centered monthly total."""
    fig = go.Figure(go.Pie(
        labels=list(expenses), values=list(expenses.values()), hole=0.68,
        sort=False, direction="clockwise", textinfo="none",
        marker=dict(colors=[CATEGORY_COLORS[name] for name in expenses], line=dict(width=0)),
        hovertemplate="%{label}<br>CAD $%{value:,.0f} / month<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        template="plotly_white", height=320,
        font=dict(family="IBM Plex Sans, Arial, sans-serif", size=12, color="#343541"),
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        hoverlabel=dict(bgcolor="white", font_color="#343541"),
        separators=".,",
        margin=dict(l=16, r=16, t=16, b=16), showlegend=False,
        annotations=[
            dict(x=0.5, y=0.54, xref="paper", yref="paper", showarrow=False,
                 xanchor="center", yanchor="middle", align="center",
                 text=f"<b>${sum(expenses.values()):,.0f}</b>", font_size=24),
            dict(x=0.5, y=0.43, xref="paper", yref="paper", showarrow=False,
                 xanchor="center", yanchor="middle", align="center",
                 text="CAD per month", font=dict(size=12, color="#77808f")),
        ],
    )
    fig.update_traces(domain=dict(x=[0, 1], y=[0, 1]))
    return fig


def reference_budget_figure():
    """Pair the composition graphic with an exact, accessible category summary."""
    with st.container(key="figure_reference_budget"):
        chart, summary = st.columns([1, 1.15], gap="large", vertical_alignment="center")
        with chart:
            st.plotly_chart(expense_donut(REFERENCE), width="stretch", config=PLOT_CONFIG,
                            theme=None, key="reference_expenses")
        with summary:
            rows = "".join(
                f'<tr><th scope="row"><span class="expense-swatch" '
                f'style="background-color:{CATEGORY_COLORS[name]}" aria-hidden="true"></span>'
                f'{escape(name)}</th><td>${value:,.0f}</td></tr>'
                for name, value in REFERENCE.items()
            )
            st.html(
                '<table class="expense-summary"><caption>Reference student budget · CAD per month</caption>'
                '<thead><tr><th scope="col">Category</th><th scope="col">Monthly cost</th></tr></thead>'
                f'<tbody>{rows}</tbody><tfoot><tr><th scope="row">Total</th>'
                f'<td>${sum(REFERENCE.values()):,.0f}</td></tr></tfoot></table>'
            )
        st.caption(f"Source: [University of Waterloo, living costs and housing]({WATERLOO}), "
                   "monthly estimates checked October 21, 2026. Housing uses the $950 lower bound; "
                   "transport is additional to UPass. Publication year is not specified on the table.")


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


def main():
    st.set_page_config(
        page_title="Dat Duong",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.html(f"<style>{(ROOT / 'style.css').read_text(encoding='utf-8')}</style>")
    try:
        domestic, international, graduate = load_tuition()
    except (OSError, ValueError, KeyError) as error:
        st.error(f"The original tuition CSV files could not be loaded: {error}")
        st.stop()
    first, latest = int(domestic.index.min()), int(domestic.index.max())
    du = int(domestic.loc[latest, "Canadian undergraduate students"])
    iu = int(international.loc[latest, "International undergraduate students"])
    dg = int(domestic.loc[latest, "Canadian graduate students"])
    ig = int(international.loc[latest, "International graduate students"])
    first_gap = int(international.loc[first, "International undergraduate students"]
                    - domestic.loc[first, "Canadian undergraduate students"])
    provinces = graduate.drop(index="Canada")

    with st.container(key="story", horizontal_alignment="center"):
        with st.container(width=CONTENT_WIDTH):
            st.title("Cost of Living in Canada")
            st.caption("The Financial Reality of International Students")
            prose("Studying abroad is an exciting opportunity, but moving to a new country also mean that you have to learn how to manage life in a country where you know nobody. "
                  "As an international student in Canada, I have come to realize that the cost of education goes far beyond university tuition. "
                  "From finding a place to live to buying groceries and getting around the city, everyday expenses quickly become part of my experience. ")
            prose("In this story, I want to explore what it really costs to study and live in Canada. Using official statistics (mostly by Canada Goverment)"
                  "to look at the financial challenges international students like myself face and the decisons that come with them.")
            st.image(str(ROOT / "nathan_philips.jpg"), width="stretch")
            st.header("Part I: The Price of Education")
            prose("When I first considered studying in Canada, tuition was one of the biggest expenses I had to think about. "
                  "I knew international students generally paid more than domestic students"
                  "but I wanted to understand just how large that difference was and how it had changed overtime.")
            prose("The chart below compares average tuition fees for domestic and international undergraduate and graduate students "
                  "from the academic year **2015/2016** to **2025/2026**. The line chart reveals how differently tuition costs have changed for the groups over the past decade.")

        with st.container(width=CONTENT_WIDTH, key="tuition_figure"):
            tableau("tuition_trend.png")
        with st.container(width=CONTENT_WIDTH):
            prose('In **2025/2026**, the average international undergraduate tuition fee reached '
                  '<span class="tuition-international-undergraduate">$41,746</span> per year, '
                  'while domestic students paid <span class="tuition-domestic-undergraduate">$7,734</span> on average. '
                  "That's roughly 5.4 times higher. The difference has also grown over time, making tuition an inreasingly important financial consideration for students coming abroad. "
                  'For graduate students, the gap is also significant. International students paid an average of '
                  '<span class="tuition-international-graduate">$24,028</span> compared to '
                  '<span class="tuition-domestic-graduate">$7,978</span> for domestic students.',
                  allow_html=True)
            prose("But tuition isn't the same everywhere in Canada. Where a student choose to study can also make a big difference.")

            st.subheader("Where You Study Matters")
            prose("A national average can hide considerable variation. These maps compare annual graduate tuition "
                  "for **2025/2026** across the ten provinces in the supplied data. Switch student groups to see how "
                  "the comparison changes.")
        with st.container(width=CONTENT_WIDTH):
            group = st.segmented_control("Compare graduate tuition", ["International", "Domestic"],
                                         default="International", key="map_group")
            tableau("domestic_tuition_map.png" if group == "Domestic" else "international_tuition_map.png")
        with st.container(width=CONTENT_WIDTH):
            high = provinces["International students"].idxmax()
            low = provinces["International students"].idxmin()
            prose(f"Ontario has the highest international graduate average among the ten provinces, at "
                  f"${provinces.loc[high, 'International students']:,}; {low} has the lowest, at "
                  f"${provinces.loc[low, 'International students']:,}. Ontario's domestic graduate average is "
                  f"${provinces.loc['Ontario', 'Canadian students']:,}. These provincial comparisons exclude "
                  "the Canada aggregate and do not describe undergraduate tuition.")
            prose("But tuition is only part of the financial commitment. Once students arrive in Canada, "
                  "another set of expenses becomes part of their everyday lives.")

            st.header("Part II: Beyond Tuition")
            prose("Before arrival, students need to demonstrate that they have funds for daily life. "
                  "After arrival, those funds become a series of recurring expenses.")
            st.subheader("A financial starting point")
            st.html(
                '<section class="ircc-stat" aria-label="Living-expense proof of funds">'
                '<div class="ircc-stat-context">Living-expense proof of funds · one person outside Quebec</div>'
                '<div class="ircc-stat-number">$1,954</div>'
                '<div class="ircc-stat-unit">CAD per month</div>'
                '<div class="ircc-stat-details">Annual requirement: $23,448 · '
                'Effective date: September 1, 2026</div>'
                '</section>'
            )
            prose("This is an immigration proof-of-funds requirement for applications submitted on or after "
                  "that date, not a government-prescribed spending budget. Tuition and transportation to and "
                  "from Canada are additional.")
            st.caption(f"Source: [IRCC, proof of financial support]({IRCC}); annual amount divided by 12. "
                       "Monthly equivalent of the annual requirement. Source checked October 21, 2026.")
            st.subheader("Estimated Monthly Living Expenses")
            prose("Published university cost estimates offer a useful starting point for planning a student "
                  "budget in Canada. This illustrative monthly living-expense scenario uses the University "
                  "of Waterloo's expense categories and the lower end of its housing range: "
                  "**$2,121 per month**.")
            prose("Use this as a reference student budget, not a Canadian national average. The underlying "
                  "estimates are for a single person in Waterloo; actual spending varies by city, housing "
                  "arrangement and personal habits.")
            reference_budget_figure()
            prose("The reference student budget is **$167 above** the IRCC monthly equivalent. The comparison "
                  "is illustrative: the figures have different purposes and scopes. Neither includes tuition, "
                  "and the reference budget excludes the university's listed one-time setup costs. No inflation adjustment "
                  "aligns the two sources.")
            st.subheader("My Monthly Expenses")
            prose("**Personal data to be added.** This space is reserved for my actual housing, groceries, "
                  "transportation, phone and miscellaneous expenses. Published estimates above are separate "
                  "from my personal spending.")
            prose("Published estimates provide a starting point. Your housing arrangement, day-to-day spending "
                  "and access to paid work will shape the budget you actually have to manage.")

            st.header("Part III: Making Ends Meet")


if __name__ == "__main__":
    main()
