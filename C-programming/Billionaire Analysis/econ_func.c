#include <stdio.h>
#include <math.h>

// Billionaire Density
double BillionaireDensity(int born, double populationMillions) {

  if (populationMillions <= 0) {
    return 0.0;
  }
  return (double)born / populationMillions;
}

// Drain Rate
double DrainRate(int left, int born) {

  if (born <= 0) {
    return 0.0;
  }
  return (double)left / born;
}

// Per Capita Income
double PerCapitaIncome(double totalIncome, double population) {

  if (population <= 0) {
    return 0.0;
  }
  return totalIncome / population;
}

// General Growth Rate
double GrowthRate(double current, double previous) {

  if (previous <= 0) {
    return 0.0;
  }
  return ((current - previous) / previous) * 100.0;
}

// Wealth Growth
double WealthGrowth(double gdpCurrent, double gdpPrevious) {

  if (gdpPrevious <= 0) {
    return 0.0;
  }
  return (gdpCurrent - gdpPrevious) / gdpPrevious;
}

// Drain Intensity
double DrainIntensity(int studentsOut, double population) {

  if (population <= 0) {
    return 0.0;
  }  
  return (double)studentsOut / population;
}