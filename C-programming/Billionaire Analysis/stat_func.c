#include <stdio.h>
#include <math.h>
#include <stdlib.h>

/*Basic Math Utilities*/

// the total sum of an array.

double Sum(double data[], int n) {
  double total = 0;
  for (int i = 0; i < n; i++) {
    total += data[i];
  }
  return total;
}

// the Average (Mean).

double Mean(double data[], int n) {

  if (n <= 0) { 
    return 0.0;
  }
  else {
    return Sum(data, n) / n;
  } 

}

/*Stability & Spread Analysis */

// Variance to measure fluctuation.
double Variance(double data[], int n) {
  if (n <= 0) {
    return 0.0;
  }

  double mean = Mean(data, n);
  double sqDiff = 0;
  
  for (int i = 0; i < n; i++) {
    sqDiff += pow(data[i] - mean, 2);
  }

  return sqDiff / n;
}

// Standard Deviation (Sigma).

double StandardDeviation(double data[], int n, double mean) {

  if (n <= 0) {
    return 0.0;
  }
  
  return sqrt(Variance(data, n));
}

/* Bivariate Analysis*/

// Pearson Correlation Coefficient (r).

double PearsonR(double x[], double y[], int n) {

  if (n <= 0) {
    return 0.0;
  }
  
  double sumX = Sum(x, n);
  double sumY = Sum(y, n);
  double sumXY = 0, sumX2 = 0, sumY2 = 0;
  
  for (int i = 0; i < n; i++) {
    sumXY += x[i] * y[i];       
    sumX2 += x[i] * x[i];       
    sumY2 += y[i] * y[i];       
  }
  
  // Formula for Pearson r
  double numerator = (n * sumXY) - (sumX * sumY);
  double denominator = sqrt((n * sumX2 - pow(sumX, 2)) * (n * sumY2 - pow(sumY, 2)));
  
  if (denominator == 0) {
    return 0;
  } 

  return numerator / denominator;
}

// Linear Regression Analysis
// (y = mx + c) 
void LinearRegression(double x[], double y[], int n) {

  if (n <= 0) {
    return;
  }
  
  double sumX = Sum(x, n);
  double sumY = Sum(y, n);
  double sumXY = 0, sumX2 = 0;
  
  for (int i = 0; i < n; i++) {
    sumXY += x[i] * y[i];
    sumX2 += x[i] * x[i];
  }
  
  // Calculating Slope (m) and Y-Intercept (c)
  double denominator = (n * sumX2 - sumX * sumX);
  
  if (denominator == 0) {
    printf("Error: Cannot calculate regression line (vertical line).\n");
    return;
  }
  
  double m = (n * sumXY - sumX * sumY) / denominator;
  double c = (sumY - m * sumX) / n;
  
  printf("\n--- Linear Regression Model ---\n");
  printf("Slope (m):     %.4f\n", m);
  printf("Intercept (c): %.4f\n", c);
  printf("Equation:      y = %.4fx + %.4f\n", m, c);
  printf("-------------------------------\n");
}

/* Distribution Analysis*/

// Sorts array (Bubble Sort).
// for median and quartile
void SortArray(double data[], int n) {
  for (int i = 0; i < n - 1; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (data[j] > data[j + 1]) {
        double temp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = temp;
      }
    }
  }
}

double Median(double arr[], int n) {
  SortArray(arr, n);
  if(n % 2 == 0) {
    return (arr[n/2 - 1] + arr[n/2]) / 2.0;
  }
  else {
    return arr[n/2];
  }
}

double Quartile(double arr[], int n, int q_num) {
  SortArray(arr, n);
  
  if (q_num == 2) {
    return Median(arr, n);
  }
  
  int mid = n / 2;
  
  if (q_num == 1) {
    return Median(arr, mid);
  }
  
  if (q_num == 3) {
    if (n % 2 == 0) {
      return Median(arr + mid, mid);
    }
    else {
      return Median(arr + mid + 1, mid);
    }
  }
  
  return -1; // Return error if q_num is not 1, 2, or 3
}

// Prints a BoxPlot summary (Min, Q1, Median, Q3, Max).

void BoxPlot(double sorted_data[], int n) {

    if (n <= 0) {
        printf("Error: Empty dataset.\n");
        return;
    }

    double min = sorted_data[0];
    double q1  = Quartile(sorted_data, n, 1);
    double q2  = Quartile(sorted_data, n, 2); // Median
    double q3  = Quartile(sorted_data, n, 3);
    double max = sorted_data[n - 1];

    printf("\n--- Accurate BoxPlot Summary ---\n");
    printf("Minimum:    %.2f\n", min);
    printf("Q1 (25%%):   %.2f\n", q1);
    printf("Median:     %.2f\n", q2);
    printf("Q3 (75%%):   %.2f\n", q3);
    printf("Maximum:    %.2f\n", max);
    printf("IQR:        %.2f\n", q3 - q1);
    printf("--------------------------------\n");
}

// Skewness.
// if the income distribution leans to the left or right.
double Skewness(double data[], int n, double mean, double stdDev) {
  if (n <= 0 || stdDev == 0) {
    return 0.0;
  }
  
  double sum_cubed = 0;
  for (int i = 0; i < n; i++) {
    sum_cubed += pow((data[i] - mean) / stdDev, 3);
  }

  return sum_cubed / n;
}

// Kurtosis.
// peakedness or heavy tails (outliers) in the data.
double Kurtosis(double data[], int n, double mean, double stdDev) {
  if (n <= 0 || stdDev == 0) {
    return 0.0;
  }
  
  double sum_fourth = 0;
  for (int i = 0; i < n; i++) {
    sum_fourth += pow((data[i] - mean) / stdDev, 4);
  }

  return (sum_fourth / n) - 3;
}