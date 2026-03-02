#ifndef STATISTICS_H
#define STATISTICS_H

// Basic Math Utilities
double Sum(double data[], int n);
double Mean(double data[], int n);

// Stability & Spread Analysis
double Variance(double data[], int n);
double StandardDeviation(double data[], int n, double mean);

// Bivariate Analysis
double PearsonR(double x[], double y[], int n);
void LinearRegression(double x[], double y[], int n);

// Distribution Analysis
void SortArray(double data[], int n);
double Median(double arr[], int n);
double Quartile(double arr[], int n, int q_num);
void BoxPlot(double sorted_data[], int n);
double Skewness(double data[], int n, double mean, double stdDev);
double Kurtosis(double data[], int n, double mean, double stdDev);

#endif