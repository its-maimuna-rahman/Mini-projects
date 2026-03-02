#ifndef ECONOMICS_H
#define ECONOMICS_H

// Economic Analysis Functions
double BillionaireDensity(int born, double populationMillions);
double DrainRate(int left, int born);
double PerCapitaIncome(double totalIncome, double population);
double GrowthRate(double current, double previous);
double WealthGrowth(double gdpCurrent, double gdpPrevious);
double DrainIntensity(int studentsOut, double population);

#endif