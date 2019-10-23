package dev.nogipx.java.problems.test;

import dev.nogipx.java.problems.IntegerReducer;
import dev.nogipx.java.problems.MultifunctionalMapper;
import org.junit.Test;

import java.util.Arrays;
import java.util.List;
import java.util.function.UnaryOperator;

import static org.junit.Assert.assertEquals;


public class JavaFunctionalStepikTest {

  @Test
  public void mapperTest() {
    UnaryOperator<List<Integer>> incrementer =
      MultifunctionalMapper.multifunctionalMapper.apply(Arrays.asList(x -> x+1, x->x+1));

    List<Integer> mTaO = MultifunctionalMapper.multTwoAndThenAddOneTransformation.apply(List.of(1,2,3));
    List<Integer> sE = MultifunctionalMapper.squareAndThenGetNextEvenNumberTransformation.apply(List.of(1,2,3));

    assertEquals(List.of(3,3,3), incrementer.apply(List.of(1,1,1)));
    assertEquals(List.of(3,5,7), mTaO);
    assertEquals(List.of(2,6,10), sE);
  }

  @Test
  public void reducerTest() {
    int sum1 = IntegerReducer.sumOperator.applyAsInt(1, 4);
    int sum2 = IntegerReducer.sumOperator.applyAsInt(5, 6);
    int prod1 = IntegerReducer.productOperator.applyAsInt(1, 4);
    int prod2 = IntegerReducer.productOperator.applyAsInt(5, 6);

    assertEquals(10, sum1);
    assertEquals(24, prod1);
    assertEquals(11, sum2);
    assertEquals(30, prod2);
  }

}
