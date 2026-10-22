# Storyboard documentation outline

These seven notes are prompts for your submission, not a claim that undocumented design iterations took place. Replace the personal placeholders and record actual feedback as you develop the project.

1. **Theme and rationale.** Introduce the question: what does it really cost to pursue an education in Canada as an international student? Explain why tuition alone provides an incomplete picture and why a continuous editorial story suits the topic.

2. **Main character and personal connection.** Identify yourself as an international student studying in Ontario. [Add your actual program, relevant experiences and financial decisions.] Explain how your perspective connects national statistics to daily life without suggesting your experience represents all students.

3. **Target audience.** Address prospective international students and their families first, with Canadian students and other readers as a secondary audience. Explain the choice of plain language, brief interpretations and adjustable examples.

4. **Sources and visualization selection.** Describe the four supplied tuition CSVs and the three unchanged Tableau exports. Explain the time-series comparison, the graduate tuition maps, the IRCC annual requirement expressed monthly, the Waterloo-based reference expense donut and category table. Distinguish averages, published estimates, scenarios and personal data. Note that the Statistics Canada site was unavailable during implementation; calculations use the supplied extracts.

5. **First design concept to compare — sequential evidence.** Sketch an article with all three Tableau images shown one after another and explanatory text between them. Evaluate reading order, image size and whether consecutive maps create too much scrolling. [Record whether you actually prototyped this, with dated screenshots and feedback.]

6. **Second and final concepts to compare.** Concept two: place the two provincial maps side by side, keeping the tuition trend above them; evaluate whether geographic labels remain legible. Concept three: use a shared full-width map with a compact student-group switch and an expense donut paired with a compact summary table. The current prototype implements concept three, using Movies-inspired serif headings, a shared 1080px content width, light native controls and brighter Plotly colours. [Document your actual comparison, revisions and reasons for choosing a final version; do not present untested concepts as completed iterations.]

7. **Final storytelling approach and takeaway.** Explain the four-part progression: the price of education, everyday costs, making ends meet and the human experience. Part III is currently a heading reserved for content to be added later. [Add your own reflection.] End with the intended takeaway that affordability involves continuing decisions about time and resources, beyond admission and tuition.

## Running the prototype

From this project directory:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The four CSVs and three PNGs must remain alongside `app.py`. `.streamlit/config.toml` supplies the native light theme and blue widget accent; custom visual styling is in `style.css`.

## Updating personal information

Replace the explicitly marked paragraphs under **My Monthly Expenses** and **Part IV: Beyond the Numbers** when actual data and reflections are available. Do not replace published reference estimates with personal values. The reference budget totals $2,121 per month. The calculator has been removed; the Part III heading is reserved for future content.

## Design reference

[Streamlit Movies source](https://github.com/streamlit/demo-movies) and its [theme configuration](https://github.com/streamlit/demo-movies/blob/main/.streamlit/config.toml): IBM Plex Serif headings, compact sans-serif body text, a 700px reading measure, wider comparison content and blue widget accents. Fonts load from Google Fonts with Georgia and Segoe UI/Arial fallbacks. The live demo redirected to authentication during inspection; the source and supplied screenshots informed the implementation.
