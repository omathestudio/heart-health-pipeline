-- Heart Health Pipeline: analysis questions
-- Every rate is weighted by survey_weight so it represents the US adult population.
-- Each query starts with a "-- name:" line so Python can find it by name.


-- name: overall_rate
-- What share of US adults have had heart disease or a heart attack?
SELECT
    COUNT(*) AS respondents,
    ROUND(100.0 * SUM(heart_disease * survey_weight) / SUM(survey_weight), 1) AS heart_disease_pct
FROM respondents
WHERE heart_disease IS NOT NULL;


-- name: by_age_sex
-- How does heart disease change with age, for men and women?
SELECT
    age_group,
    sex,
    COUNT(*) AS respondents,
    ROUND(100.0 * SUM(heart_disease * survey_weight) / SUM(survey_weight), 1) AS heart_disease_pct
FROM respondents
WHERE heart_disease IS NOT NULL
  AND age_group IS NOT NULL
GROUP BY age_group, sex
ORDER BY age_group, sex;


-- name: by_risk_factor
-- Heart disease rate for people with vs without each risk factor.
WITH factors AS (
    SELECT 'High blood pressure' AS risk_factor, high_bp AS has_factor, heart_disease, survey_weight FROM respondents
    UNION ALL
    SELECT 'High cholesterol', high_cholesterol, heart_disease, survey_weight FROM respondents
    UNION ALL
    SELECT 'Diabetes', diabetes, heart_disease, survey_weight FROM respondents
    UNION ALL
    SELECT 'Current smoker',
           CASE WHEN smoking_status LIKE 'Current%' THEN 1
                WHEN smoking_status IS NOT NULL THEN 0 END,
           heart_disease, survey_weight FROM respondents
    UNION ALL
    SELECT 'No exercise', inactive, heart_disease, survey_weight FROM respondents
    UNION ALL
    SELECT 'Heavy drinker', heavy_drinker, heart_disease, survey_weight FROM respondents
)
SELECT
    risk_factor,
    CASE has_factor WHEN 1 THEN 'Yes' ELSE 'No' END AS has_factor,
    COUNT(*) AS respondents,
    ROUND(100.0 * SUM(heart_disease * survey_weight) / SUM(survey_weight), 1) AS heart_disease_pct
FROM factors
WHERE has_factor IS NOT NULL
  AND heart_disease IS NOT NULL
GROUP BY risk_factor, has_factor
ORDER BY risk_factor, has_factor DESC;


-- name: by_state
-- Which states have the highest heart disease rates?
SELECT
    state_fips,
    COUNT(*) AS respondents,
    ROUND(100.0 * SUM(heart_disease * survey_weight) / SUM(survey_weight), 1) AS heart_disease_pct
FROM respondents
WHERE heart_disease IS NOT NULL
GROUP BY state_fips
ORDER BY heart_disease_pct DESC;


-- name: risk_factor_count
-- Does risk add up? Heart disease rate by how many of 5 risk factors a person has.
WITH counted AS (
    SELECT
        heart_disease,
        survey_weight,
        high_bp + high_cholesterol + diabetes + inactive
          + CASE WHEN smoking_status LIKE 'Current%' THEN 1 ELSE 0 END AS num_risk_factors
    FROM respondents
    WHERE heart_disease IS NOT NULL
      AND high_bp IS NOT NULL
      AND high_cholesterol IS NOT NULL
      AND diabetes IS NOT NULL
      AND inactive IS NOT NULL
      AND smoking_status IS NOT NULL
)
SELECT
    num_risk_factors,
    COUNT(*) AS respondents,
    ROUND(100.0 * SUM(heart_disease * survey_weight) / SUM(survey_weight), 1) AS heart_disease_pct
FROM counted
GROUP BY num_risk_factors
ORDER BY num_risk_factors;