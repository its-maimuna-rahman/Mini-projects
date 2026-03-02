#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "statistics.h"
#include "economics.h"

#define MAX_COUNTRIES 200
#define MAX_YEARS 100
#define MAX_LINE 1024

// Structure to hold country data from world.csv
typedef struct {
    char country[200];
    double avg_education;
    double avg_salary;
    double income_with_billionaire;
    double population_with_billionaire;
    double income_without_billionaire;
    double population_without_billionaire;
    int billionaire_left;
    int billionaire_born;
} CountryData;

// Structure for Bangladesh data
typedef struct {
    int year;
    double gdp_per_capita;
    double population;
    int students_out;
} BangladeshData;

// Function prototypes
int loadCountryData(const char* filename, CountryData countries[]);
int loadBangladeshData(const char* filename, BangladeshData bd_data[]);
void analysis1_PerCapitaIncome(CountryData countries[], int n);
void analysis2_BillionaireEffects(CountryData countries[], int n);
void analysis3_BrainDrainBillionaireDensity(CountryData countries[], int n);
void analysis4_BangladeshCaseStudy(BangladeshData bd_data[], int n);

// Load country data from world.csv
int loadCountryData(const char* filename, CountryData countries[]) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open file %s\n", filename);
        return 0;
    }
    
    char line[MAX_LINE];
    int count = 0;
    
    // Skip header line
    fgets(line, MAX_LINE, file);
    
    while (fgets(line, MAX_LINE, file) && count < MAX_COUNTRIES) {
        // Parse CSV line
        char* token = strtok(line, ",");
        if (!token) continue;
        
        strcpy(countries[count].country, token);
        
        token = strtok(NULL, ",");
        countries[count].avg_education = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].avg_salary = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].income_with_billionaire = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].population_with_billionaire = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].income_without_billionaire = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].population_without_billionaire = atof(token);
        
        token = strtok(NULL, ",");
        countries[count].billionaire_left = atoi(token);
        
        token = strtok(NULL, ",");
        countries[count].billionaire_born = atoi(token);
        
        count++;
    }
    
    fclose(file);
    return count;
}

// Load Bangladesh data from banglaesh.csv
int loadBangladeshData(const char* filename, BangladeshData bd_data[]) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        printf("Error: Could not open file %s\n", filename);
        return 0;
    }
    
    char line[MAX_LINE];
    int count = 0;
    
    // Skip header line
    fgets(line, MAX_LINE, file);
    
    while (fgets(line, MAX_LINE, file) && count < MAX_YEARS) {
        char* token = strtok(line, ",");
        if (!token) continue;
        
        bd_data[count].year = atoi(token);
        
        token = strtok(NULL, ",");
        bd_data[count].gdp_per_capita = atof(token);
        
        token = strtok(NULL, ",");
        bd_data[count].population = atof(token);
        
        token = strtok(NULL, ",");
        bd_data[count].students_out = atoi(token);
        
        count++;
    }
    
    fclose(file);
    return count;
}

// ANALYSIS 1: Per Capita Income Regression (Education vs Salary)
void analysis1_PerCapitaIncome(CountryData countries[], int n) {
    printf("\n\n");
    printf("============================================================================================================\n");
    printf("                            ANALYSIS 1: PER CAPITA INCOME REGRESSION                                        \n");
    printf("============================================================================================================\n");
    printf("\nBivariate Analysis: Average years of education (X) vs Average Annual salary (Y)\n");
    printf("Total data points: %d countries\n\n", n);
    
    // Prepare data arrays
    double x_data[MAX_COUNTRIES];  // Education
    double y_data[MAX_COUNTRIES];  // Salary
    
    for (int i = 0; i < n; i++) {
        x_data[i] = countries[i].avg_education;
        y_data[i] = countries[i].avg_salary;
    }
    
    // Display country-wise data
    printf("Country-wise Data Points:\n");
    printf("%-20s %20s %20s\n", "Country", "Education (Years)", "Salary (Annual)");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    for (int i = 0; i < n; i++) {
        printf("%-20s %20.2f %20.2f\n", 
               countries[i].country, 
               countries[i].avg_education, 
               countries[i].avg_salary);
    }
    
    // Perform linear regression
    printf("\n");
    LinearRegression(x_data, y_data, n);
    
    // Calculate correlation coefficient
    double correlation = PearsonR(x_data, y_data, n);
    printf("\nCorrelation Coefficient (r): %.4f\n", correlation);
    
    // Interpret correlation
    printf("\nInterpretation: ");
    if (fabs(correlation) > 0.8) {
        printf("VERY STRONG positive relationship between education and salary.\n");
    } else if (fabs(correlation) > 0.6) {
        printf("STRONG positive relationship between education and salary.\n");
    } else if (fabs(correlation) > 0.4) {
        printf("MODERATE positive relationship between education and salary.\n");
    } else {
        printf("WEAK relationship between education and salary.\n");
    }
}

// ANALYSIS 2: Billionaire Effects (Univariate Analysis)
void analysis2_BillionaireEffects(CountryData countries[], int n) {
    printf("\n\n");
    printf("============================================================================================================\n");
    printf("                               ANALYSIS 2: BILLIONAIRE EFFECTS ANALYSIS                                     \n");
    printf("============================================================================================================\n");
    printf("\nUnivariate Analysis: Impact of Billionaires on National Income Distribution\n\n");
    
    double avg_income_with[MAX_COUNTRIES];
    double avg_income_without[MAX_COUNTRIES];
    
    // Part 1: Calculate average income WITH billionaires
    printf("*************** PART 1: Average National Income WITH Billionaires **************\n\n");
    printf("%-20s %25s %20s %25s\n", 
           "Country", "Total Income (with)", "Population (with)", "Avg Income (with)");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    
    for (int i = 0; i < n; i++) {
        avg_income_with[i] = PerCapitaIncome(
            countries[i].income_with_billionaire,
            countries[i].population_with_billionaire
        );
        printf("%-20s %25.2f %20.2f %25.2f\n",
               countries[i].country,
               countries[i].income_with_billionaire,
               countries[i].population_with_billionaire,
               avg_income_with[i]);
    }
    
    // Sort for outlier detection
    double sorted_with[MAX_COUNTRIES];
    for (int i = 0; i < n; i++) {
        sorted_with[i] = avg_income_with[i];
    }
    SortArray(sorted_with, n);
    
    // Outlier detection using 3*IQR method
    double Q1 = sorted_with[n/4];
    double Q3 = sorted_with[3*n/4];
    double IQR = Q3 - Q1;
    double lower_bound = Q1 - 3 * IQR;
    double upper_bound = Q3 + 3 * IQR;
    
    printf("\n******************************** Outlier Detection (3*IQR Method) ********************************\n\n");
    printf("Q1 (25th percentile): %.2f\n", Q1);
    printf("Q3 (75th percentile): %.2f\n", Q3);
    printf("IQR (Q3 - Q1): %.2f\n", IQR);
    printf("Lower Bound (Q1 - 3*IQR): %.2f\n", lower_bound);
    printf("Upper Bound (Q3 + 3*IQR): %.2f\n", upper_bound);
    
    printf("\nOutliers detected:\n");
    int outlier_count = 0;
    for (int i = 0; i < n; i++) {
        if (avg_income_with[i] < lower_bound || avg_income_with[i] > upper_bound) {
            printf("  - %s: %.2f", countries[i].country, avg_income_with[i]);
            if (avg_income_with[i] > upper_bound) {
                printf(" (UPPER EXTREME)\n");
            } else {
                printf(" (LOWER EXTREME)\n");
            }
            outlier_count++;
        }
    }
    printf("Total outliers: %d\n", outlier_count);
    
    // Distribution statistics WITH billionaires
    double mean_with = Mean(avg_income_with, n);
    double std_dev_with = StandardDeviation(avg_income_with, n, mean_with);
    double skew_with = Skewness(avg_income_with, n, mean_with, std_dev_with);
    double kurt_with = Kurtosis(avg_income_with, n, mean_with, std_dev_with);
    
    printf("\n*************************** Distribution Statistics (WITH Billionaires) *****************************\n\n");
    printf("Mean: %.2f\n", mean_with);
    printf("Standard Deviation: %.2f\n", std_dev_with);
    printf("Skewness (Gamma 1): %.4f\n", skew_with);
    if (skew_with > 0) {
        printf("  Interpretation: Positively skewed (right-tailed distribution)\n");
    } else if (skew_with < 0) {
        printf("  Interpretation: Negatively skewed (left-tailed distribution)\n");
    } else {
        printf("  Interpretation: Symmetric distribution\n");
    }
    
    printf("\nKurtosis (Gamma 2): %.4f\n", kurt_with);
    if (kurt_with > 0) {
        printf("  Interpretation: Leptokurtic (heavy-tailed, sharp peak)\n");
    } else if (kurt_with < 0) {
        printf("  Interpretation: Platykurtic (light-tailed, flat peak)\n");
    } else {
        printf("  Interpretation: Mesokurtic (normal distribution)\n");
    }
    
    // Part 2: Calculate average income WITHOUT billionaires
    printf("\n\n********************** PART 2: Average National Income WITHOUT Billionaires **********************\n\n");
    printf("%-20s %28s %23s %28s\n", 
           "Country", "Total Income (without)", "Population (without)", "Avg Income (without)");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    
    for (int i = 0; i < n; i++) {
        avg_income_without[i] = PerCapitaIncome(
            countries[i].income_without_billionaire,
            countries[i].population_without_billionaire
        );
        printf("%-20s %28.2f %23.2f %28.2f\n",
               countries[i].country,
               countries[i].income_without_billionaire,
               countries[i].population_without_billionaire,
               avg_income_without[i]);
    }
    
    // Distribution statistics WITHOUT billionaires
    double mean_without = Mean(avg_income_without, n);
    double std_dev_without = StandardDeviation(avg_income_without, n, mean_without);
    double skew_without = Skewness(avg_income_without, n, mean_without, std_dev_without);
    double kurt_without = Kurtosis(avg_income_without, n, mean_without, std_dev_without);
    
    printf("\n********** Distribution Statistics (WITHOUT Billionaires) **********\n\n");
    printf("Mean: %.2f\n", mean_without);
    printf("Standard Deviation: %.2f\n", std_dev_without);
    printf("Skewness (Gamma 1): %.4f\n", skew_without);
    if (skew_without > 0) {
        printf("  Interpretation: Positively skewed (right-tailed distribution)\n");
    } else if (skew_without < 0) {
        printf("  Interpretation: Negatively skewed (left-tailed distribution)\n");
    } else {
        printf("  Interpretation: Symmetric distribution\n");
    }
    
    printf("\nKurtosis (Gamma 2): %.4f\n", kurt_without);
    if (kurt_without > 0) {
        printf("  Interpretation: Leptokurtic (heavy-tailed, sharp peak)\n");
    } else if (kurt_without < 0) {
        printf("  Interpretation: Platykurtic (light-tailed, flat peak)\n");
    } else {
        printf("  Interpretation: Mesokurtic (normal distribution)\n");
    }
    
    // Comparative Analysis
    printf("\n\n**************************************** COMPLETE ANALYSIS ****************************************\n\n");
    printf("Impact of Billionaires on Income Distribution:\n\n");
    
    double skewness_change = skew_with - skew_without;
    double kurtosis_change = kurt_with - kurt_without;
    
    printf("Change in Skewness (Gamma 1): %.4f\n", skewness_change);
    if (skewness_change > 0) {
        printf("  => Billionaires INCREASE right-skewness (more extreme high incomes)\n");
    } else {
        printf("  => Billionaires DECREASE right-skewness\n");
    }
    
    printf("\nChange in Kurtosis (Gamma 2): %.4f\n", kurtosis_change);
    if (kurtosis_change > 0) {
        printf("  => Billionaires CREATE extreme values (heavier tails)\n");
    } else {
        printf("  => Billionaires REDUCE extreme value concentration\n");
    }
    
    double income_inflation = ((mean_with - mean_without) / mean_without) * 100;
    
    printf("\nAverage Income WITH billionaires: %.2f\n", mean_with);
    printf("Average Income WITHOUT billionaires: %.2f\n", mean_without);
    printf("Income Inflation due to Billionaires: %.2f%%\n", income_inflation);
    
    if (income_inflation > 10) {
        printf("\nCONCLUSION: Billionaires SIGNIFICANTLY INFLATE average income!\n");
        printf("This suggests high income inequality - the ultra-rich skew the mean upward.\n");
    } else {
        printf("\nCONCLUSION: Billionaires have MODERATE impact on average income.\n");
    }
}

// ANALYSIS 3: Relation of Brain Drain with Billionaire Density
void analysis3_BrainDrainBillionaireDensity(CountryData countries[], int n) {
    printf("\n\n");
    printf("============================================================================================================\n");
    printf("                         ANALYSIS 3: BRAIN DRAIN vs BILLIONAIRE DENSITY CORRELATION                         \n");
    printf("============================================================================================================\n");
    printf("\nBivariate Analysis: Billionaire Density (X) vs Brain Drain Rate (Y)\n\n");
    
    double x_density[MAX_COUNTRIES];    // Billionaire density
    double y_drain_rate[MAX_COUNTRIES]; // Drain rate
    
    printf("%-20s %15s %15s %20s %20s\n",
           "Country", "Population(M)", "Born", "Billionaire Density", "Drain Rate");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    
    for (int i = 0; i < n; i++) {
        // Convert population to millions (assuming it's already in appropriate units)
        double pop_millions = countries[i].population_with_billionaire / 1000000.0;
        
        x_density[i] = BillionaireDensity(
            countries[i].billionaire_born,
            pop_millions
        );
        
        y_drain_rate[i] = DrainRate(
            countries[i].billionaire_left,
            countries[i].billionaire_born
        );
        
        printf("%-20s %15.2f %15d %20.6f %20.4f\n",
               countries[i].country,
               pop_millions,
               countries[i].billionaire_born,
               x_density[i],
               y_drain_rate[i]);
    }
    
    // Calculate correlation
    double correlation = PearsonR(x_density, y_drain_rate, n);
    
    printf("\n");
    printf("Correlation Coefficient (r) between Billionaire Density and Drain Rate: %.4f\n\n", correlation);
    
    // Interpretation
    printf("INTERPRETATION:\n");
    if (correlation > 0.6) {
        printf("  => r > 0.6: STRONG POSITIVE CORRELATION\n");
        printf("  => Even though the country produces efficient people (high billionaire density),\n");
        printf("     the environment is UNABLE TO RETAIN them (high drain rate).\n");
        printf("  => This indicates a \"BRAIN DRAIN\" problem!\n");
    } else if (correlation > 0.3) {
        printf("  => 0.3 < r < 0.6: MODERATE POSITIVE CORRELATION\n");
        printf("  => There is some tendency for productive countries to lose talent.\n");
    } else if (correlation > -0.3) {
        printf("  => -0.3 < r < 0.3: WEAK OR NO CORRELATION\n");
        printf("  => Billionaire density does not strongly predict brain drain.\n");
    } else {
        printf("  => r < -0.3: NEGATIVE CORRELATION\n");
        printf("  => Countries with high billionaire density tend to RETAIN their talent.\n");
    }
    
    // Additional statistics
    double mean_density = Mean(x_density, n);
    double mean_drain = Mean(y_drain_rate, n);
    
    printf("\nSummary Statistics:\n");
    printf("  Average Billionaire Density: %.6f billionaires per million\n", mean_density);
    printf("  Average Drain Rate: %.4f (%.2f%% of billionaires leave)\n", 
           mean_drain, mean_drain * 100);
}

// ANALYSIS 4: Bangladesh Case Study - Economic Growth vs. Brain Drain
void analysis4_BangladeshCaseStudy(BangladeshData bd_data[], int n) {
    printf("\n\n");
    printf("============================================================================================================\n");
    printf("                    ANALYSIS 4: BANGLADESH CASE STUDY - ECONOMIC GROWTH vs BRAIN DRAIN                      \n");
    printf("============================================================================================================\n");
    printf("\nTime Series Analysis (1975-2025): Wealth Growth (X) vs Student Outflow (Y)\n\n");
    
    double x_wealth_growth[MAX_YEARS];
    double y_drain_intensity[MAX_YEARS];
    int analysis_count = 0;
    
    printf("%-10s %20s %20s %25s %25s\n",
           "Year", "GDP Per Capita", "Students Out", "Wealth Growth (X)", "Drain Intensity (Y)");
    printf("-------------------------------------------------------------------------------------------------------------\n");
    
    // Calculate year-over-year changes
    for (int i = 1; i < n; i++) {
        // Wealth Growth: (GDP_this_year - GDP_last_year) / GDP_last_year
        x_wealth_growth[analysis_count] = WealthGrowth(
            bd_data[i].gdp_per_capita,
            bd_data[i-1].gdp_per_capita
        );
        
        // Drain Intensity: Students_out / Population
        y_drain_intensity[analysis_count] = DrainIntensity(
            bd_data[i].students_out,
            bd_data[i].population
        );
        
        printf("%-10d %20.2f %20d %25.4f %25.6f\n",
               bd_data[i].year,
               bd_data[i].gdp_per_capita,
               bd_data[i].students_out,
               x_wealth_growth[analysis_count],
               y_drain_intensity[analysis_count]);
        
        analysis_count++;
    }
    
    // Perform correlation analysis
    double correlation = PearsonR(x_wealth_growth, y_drain_intensity, analysis_count);
    
    printf("\n");
    printf("Correlation Coefficient (r) between Wealth Growth and Student Outflow: %.4f\n\n", correlation);
    
    // Perform linear regression
    LinearRegression(x_wealth_growth, y_drain_intensity, analysis_count);
    
    // Interpretation
    printf("\nANALYSIS & INTERPRETATION:\n");
    printf("------------------------------------------------------------\n");
    
    if (correlation > 0.5) {
        printf("POSITIVE CORRELATION (r = %.4f):\n", correlation);
        printf("  => As Bangladesh's economy grows (higher GDP per capita),\n");
        printf("     MORE students leave for abroad!\n\n");
        printf("CONCLUSION:\n");
        printf("  A spiking economy in Bangladesh does NOT stop students from leaving.\n");
        printf("  Instead, it gives them MORE MONEY to buy plane tickets!\n");
        printf("  Economic growth ENABLES brain drain rather than preventing it.\n");
    } else if (correlation < -0.5) {
        printf("NEGATIVE CORRELATION (r = %.4f):\n", correlation);
        printf("  => As Bangladesh's economy grows (higher GDP per capita),\n");
        printf("     FEWER students leave for abroad!\n\n");
        printf("CONCLUSION:\n");
        printf("  Economic growth REDUCES brain drain.\n");
        printf("  Better opportunities at home keep students in Bangladesh.\n");
    } else {
        printf("WEAK CORRELATION (r = %.4f):\n", correlation);
        printf("  => Economic growth and student outflow are not strongly related.\n\n");
        printf("CONCLUSION:\n");
        printf("  Other factors beyond GDP growth drive student migration decisions.\n");
    }
    
    // Additional statistics
    double mean_growth = Mean(x_wealth_growth, analysis_count);
    double mean_drain = Mean(y_drain_intensity, analysis_count);
    
    printf("\nSummary Statistics:\n");
    printf("  Average Annual Wealth Growth: %.4f (%.2f%%)\n", mean_growth, mean_growth * 100);
    printf("  Average Drain Intensity: %.6f students per capita\n", mean_drain);
    
}

// Main function
int main() {
    CountryData countries[MAX_COUNTRIES];
    BangladeshData bd_data[MAX_YEARS];
    
    int num_countries = loadCountryData("world.csv", countries);
    int num_years = loadBangladeshData("bangladesh.csv", bd_data);
    
    if (num_countries <= 0) {
        printf("Error: Could not load country data from world.csv\n");
        return 1;
    }
    
    if (num_years <= 0) {
        printf("Error: Could not load Bangladesh data from banglaesh.csv\n");
        return 1;
    }
    
    printf("\n");
    printf("============================================================================================================\n");
    printf("                          ECONOMIC ANALYSIS: EDUCATION, WEALTH & BRAIN DRAIN STUDY                          \n");
    printf("============================================================================================================\n");
    printf("\nSuccessfully loaded:\n");
    printf("  - %d countries from world.csv\n", num_countries);
    printf("  - %d years of data from banglaesh.csv\n\n", num_years);
    
    // Perform all 4 analyses
    analysis1_PerCapitaIncome(countries, num_countries);
    analysis2_BillionaireEffects(countries, num_countries);
    analysis3_BrainDrainBillionaireDensity(countries, num_countries);
    analysis4_BangladeshCaseStudy(bd_data, num_years);
    
    printf("\n============================================================================================================\n");
    printf("                                          ALL ANALYSES COMPLETED                                              \n");
    printf("============================================================================================================\n\n");
    
    return 0;
}