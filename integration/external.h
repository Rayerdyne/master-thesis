#ifndef VENTEST_H
#define VENTEST_H

#include <iostream>

/**
 * @brief Vensim function used to get user definitions.
 * 
 */
void user_definition();

/**
 * @brief Test function, kept there for... testing 
 * 
 * @param x 
 * @param y 
 * @param z 
 * @return double the sum of the inputs
 */
double compute_a(double, double, double);

/**
 * @brief Computes the Dispa-SET appriximation by calling the surrogate model.
 * 
 * @param CapacityRatio 
 * @param ShareFlex 
 * @param ShareStorage 
 * @param ShareWind 
 * @param SharePV 
 * @param rNTC 
 * @param output_idx 
 * @return double 
 */
double compute_ds_approx(double, double, double, double, double, double, double);

#endif // VENTEST_H