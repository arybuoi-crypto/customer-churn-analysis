# Interview notes: how to explain this project

Use these notes to learn the project, not to memorize it. Run each script, read its output, and
make sure you can explain every step in your own words.

## The 30-second pitch

"I analyzed a customer churn dataset from a fictional telecom company. I cleaned the data,
calculated churn rates across customer groups, and made charts to compare the patterns. In this
sample, churn was 42.7% for month-to-month customers and 2.8% for two-year customers. That is an
association, not proof that contract type caused churn. I suggested retention ideas a company could
test and documented the limits of the data. Claude helped create the initial scripts, which I ran
and am learning to explain."

## Key concepts

| Term | Plain meaning |
|---|---|
| Churn | A customer stops paying for the service |
| Churn rate | Churned customers / all customers in the group, shown as % |
| Tenure | How many months the customer has been with the company |
| Association vs causation | "Group A churns more" is not "being in group A causes churn" |
| Confounding | A third factor linked to both things, creating a misleading pattern |
| Baseline | The overall churn rate, used to judge whether a group is high or low |
| Virtual environment | A private set of Python libraries for one project |

## What each script does, and why

### config.py
Stores folder paths and analysis choices (tenure groups, charge bands) in one place. If you change
a cut point, you change it once here. Interview angle: *"I kept assumptions in one file so they
are visible and easy to test."*

### 01_load_and_check.py
Loads the CSV and only *looks*: shape, data types, missing values, blank text, duplicates, category
values, numeric ranges. Why a separate step? You should never clean data before you have seen what
is wrong with it. Interview angle: *"I checked quality before analysis, including hidden problems
like blank text that pandas does not count as missing."*

### 02_clean_data.py
- Trims spaces in text.
- Converts `TotalCharges` to a number with `errors="coerce"`, which turns unreadable values into
  NaN instead of crashing.
- Drops rows where it could not be converted, **with a safety limit**: if more than 2% of rows
  would go, the script stops. Interview angle: *"Dropping a tiny share of rows was a judgement call,
  and I limited it and reported how many rows were removed."*
- Creates `churn_flag` (1/0). The **mean** of a 1/0 column is the share of 1s, i.e. the churn rate.
- Creates `tenure_group` and `charge_band` with `pd.cut`.
- Saves a new file; the raw file is never touched, so every step is traceable.

### 03_explore_churn.py
For each characteristic, groups customers and calculates `customers`, `churned` and
`churn_rate_pct`. It warns about small groups, compares averages of churned vs stayed customers, and
builds a contract x tenure table to check for overlap between factors.

### 04_make_charts.py
Makes the charts. Design choices you can defend:
- Bars start at zero so lengths are not exaggerated.
- One color (blue) for one measure (churn rate), so color is not decoration.
- A dashed baseline of the overall churn rate on every bar chart.
- Group sizes shown, so a rate from 80 customers is not mistaken for one from 3,000.
- Titles say *what is plotted*; the footer says the chart shows association, not cause.
- The distribution chart scales each group to 100% of its own size, so a small group is not hidden
  by a large one.
- The heatmap uses a one-hue light-to-dark scale, with white or dark text depending on the cell.

## What each chart shows, and what it does NOT prove

| Chart | Shows | Does not prove |
|---|---|---|
| Churn by contract / tenure / charges / other bars | How churn rate differs between groups | That the characteristic causes churn; also hides that groups overlap |
| Tenure and charges distributions | Whether churned and stayed customers have different shapes | The cause of those differences, or anything about individual customers |
| Contract x tenure heatmap | Whether a contract pattern holds *within* tenure groups | Causation; cells with few customers are unreliable |

## Patterns that could be misleading (check these in YOUR results)

1. **Overlapping factors.** Contract type and tenure are likely related. A pattern in one may be
   partly the other. The heatmap is there to check this.
2. **Small groups.** A high or low rate from few customers can be luck. Check the customer counts.
3. **Cut points.** Tenure groups and charge bands are my choices. Try other cut points and see
   whether the story changes.
4. **Charges and services.** Monthly charges depend on which services a customer has, so a charge
   pattern may really be a services pattern.
5. **Snapshot data.** One month of outcomes cannot show how customers' behavior changed over time.
6. **Averages hide shapes.** That is why the distribution chart exists.

## Likely interview questions (practice answering aloud)

1. **What is churn rate and how did you calculate it?**
   Churned customers divided by all customers in the group; I used the mean of a 1/0 flag.
2. **Why didn't you build a prediction model?**
   The goal was to understand and explain patterns first. A model on data I do not yet understand
   would be hard to defend. It is a possible next step.
3. **Can you say that month-to-month contracts cause churn?**
   No. I can say the groups differ in churn rate. Other factors (price, tenure, services) may
   explain part of it, and only a test could show cause.
4. **What data problems did you find, and what did you do?**
   The raw file had 7,043 rows. Eleven rows had blank `TotalCharges` values that could not be
   converted to numbers, so the cleaning step excluded them (about 0.16% of rows). The cleaned
   file has 7,032 rows. The raw CSV was kept unchanged.
5. **How would the company use your findings?**
   By testing retention actions (for example, an offer to one group with a control group) and
   measuring churn afterwards, weighing the cost of the offer against revenue kept.
6. **What are the limitations?**
   Fictional sample data, snapshot, no competitor or service-quality information, choices of cut
   points, small groups.
7. **What would you do next?**
   Test other cut points, add a statistical significance check, then consider a simple model.

## Resume bullet

Rules: include only what you did and numbers you verified in your own outputs. Do not claim impact
on a real business, because this is sample data.

> Analyzed a 7,043-row fictional telecom churn dataset using Python, pandas, Matplotlib, and
> Seaborn; cleaned the data, compared churn across customer groups, and found a 42.7% churn rate
> for month-to-month customers versus 2.8% for two-year customers; documented testable retention
> ideas and analysis limitations.

Checklist before using it:
- [x] Every number appears in `outputs/tables/` or the analysis output
- [ ] I can explain each term in the bullet in my own words
- [x] It does not claim cause, reduced churn, or a real-world outcome
- [ ] It matches the final public GitHub repository
