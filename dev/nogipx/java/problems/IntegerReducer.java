package dev.nogipx.java.problems;

import java.util.function.BiFunction;
import java.util.function.IntBinaryOperator;

public class IntegerReducer {

  /**
   * An operator that combines all values in the given range into one value
   * using combiner and initial value (seed)
   */
  public static final BiFunction<Integer, IntBinaryOperator, IntBinaryOperator> reduceIntOperator =
    (seed, reducer) -> (begin, end) -> {
      int partial = seed;
      for (int i = begin; i <= end; i++)
        partial = reducer.applyAsInt(partial, i);
      return partial;
    };

  /**
   * An operator that calculates the sum in the given range (inclusively)
   */
  public static final IntBinaryOperator sumOperator =
    reduceIntOperator.apply(0, Integer::sum);

  /**
   * An operator that calculates the product in the given range (inclusively)
   */
  public static final IntBinaryOperator productOperator =
    reduceIntOperator.apply(1, (x, y) -> x * y);
}
