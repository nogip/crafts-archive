package dev.nogipx.java.problems;

import java.util.Arrays;
import java.util.List;
import java.util.function.Function;
import java.util.function.IntUnaryOperator;
import java.util.function.UnaryOperator;
import java.util.stream.Collectors;


public class MultifunctionalMapper {

  /**
   * The function accepts a list of mappers and returns an operator that accepts a list of integers
   * and sequentially applies each mapper to each value (perform a transformation)
   */
  public static final Function<List<IntUnaryOperator>, UnaryOperator<List<Integer>>> multifunctionalMapper =
    ops -> numbers -> {
      IntUnaryOperator mapFun = ops.stream()
        .reduce(IntUnaryOperator::andThen)
        .get();
      return numbers.stream()
        .map(mapFun::applyAsInt)
        .collect(Collectors.toList());
    };

  /**
   * The operator accepts an integer list.
   * It multiplies by two each integer number and then add one to its.
   *
   * The operator returns transformed integer list.
   */
  public static final UnaryOperator<List<Integer>> multTwoAndThenAddOneTransformation =
    multifunctionalMapper.apply(Arrays.asList(x -> x*2, x -> x+1));

  public static IntUnaryOperator nextEven = (x) ->
    x % 2 == 0 ? x + 2 : x + 1;

  /**
   * The operator accepts an integer list.
   * It squares each integer number and then get the next even number following it.
   *
   * The operator returns transformed integer list.
   */
  public static final UnaryOperator<List<Integer>> squareAndThenGetNextEvenNumberTransformation =
    multifunctionalMapper.apply(Arrays.asList(x -> x*x, nextEven));
}



