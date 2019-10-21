package dev.nogipx.java.impatientcore;

import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

import java.math.BigInteger;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.LongStream;
import java.util.stream.Stream;

import static org.junit.Assert.assertEquals;


/**
 * Horstmann
 * Core JavaSE 9 for impatient
 * Chapter 8 - Streams
 */
public class StreamsChapterTest {
  private List<String> lessWords = List.of("ab abc abcd ac bcde a abcdn acde".split(" "));
  private List<String> moreWords = List.of(("Do commanded an shameless we disposing do. " +
    "Indulgence ten remarkably nor are impression out. Power is lived means oh every in we quiet. " +
    "Remainder provision an in intention. Saw supported too joy promotion engrossed propriety. " +
    "Me till like it sure no sons. Enjoyed minutes related as at on on. " +
    "Is fanny dried as often me. Goodness as reserved raptures to mistaken steepest oh screened he. " +
    "Gravity he mr sixteen esteems. Mile home its new way with high told said. " +
    "Finished no horrible blessing landlord dwelling dissuade if. Rent fond am he in on read. " +
    "Anxious cordial demands settled entered in do to colonel.")
    .replaceAll("[.]*", "")
    .split(" ")
  );

  /**
   * EX 1
   * Verify that asking for the first five long words
   * does not call the filter method once
   * the fifth long word has been found.
   * Simply log each method call.
   */
  @Test
  public void ex1VerifyLazy() {
    List<String> filtered = lessWords.stream()
      .filter(a -> a.length() > 2)
      .collect(Collectors.toList());

    assertEquals(filtered, List.of("abc abcd bcde abcdn acde".split(" ")));
  }

  /**
   * EX 2
   * Measure the difference when counting long words
   * with a parallelStream instead of a stream.
   */
  @Test
  public void ex2TestSpeedSequential() {
    long start = System.currentTimeMillis();

    List<String> filtered = moreWords.stream()
      .filter(a -> a.length() > 3)
      .collect(Collectors.toList());

    System.out.println(System.currentTimeMillis() - start);
    System.out.println(filtered);
  }

  @Test
  public void ex2TestSpeedParallel() {
    long start = System.currentTimeMillis();

    List<String> filtered = moreWords.parallelStream()
      .filter(a -> a.length() > 3)
      .collect(Collectors.toList());

    System.out.println(System.currentTimeMillis() - start);
    System.out.println(filtered);
  }

  public void ex4LinearRandomGenerator(int seed ) {}
  public void ex5() {}
  public void ex6() {}
  public void ex7() {}
  public void ex8() {}
  public void ex9() {}

  /**
   * EX 10
   * Given a finite stream of strings,
   * fing the average string length.
   */
  @Test
  public void ex10AverageLength() {
    System.out.println(moreWords);
    double avgLen = moreWords.stream()
      .mapToInt(String::length)
      .average()
      .orElse(-1);
    System.out.println("Average length of @moreWords = " + avgLen);
  }

  public void ex11() {}
  public void ex12() {}
  public void ex13() {}
  public void ex14() {}
  public void ex15() {}

  /**
   * EX 16
   * Find 500 prime numbers with 50 decimal digits,
   * using a paralel stream of BigInteger and
   * the BigInteger.isProbablePrime method.
   * Is it any faster than using a serial stream?
   */
//  @Ignore
  @Test
  public void ex16BigPrimesParallel() {
    BigInteger beginBigRange = new BigInteger(String.format("%.0f", Math.pow(10, 49)));
    long start = System.currentTimeMillis();

    List<BigInteger> nums = Stream.iterate(beginBigRange, bi -> bi.nextProbablePrime())
      .parallel()
      .limit(500)
      .collect(Collectors.toList());

    System.out.println(System.currentTimeMillis() - start);
    assertEquals(500, nums.size());
  }

//  @Ignore
  @Test
  public void ex16BigPrimesSequential() {
    BigInteger beginBigRange = new BigInteger(String.format("%.0f", Math.pow(10, 49)));
    long start = System.currentTimeMillis();

    List<BigInteger> nums = Stream.iterate(beginBigRange, bi -> bi.nextProbablePrime())
      .limit(500)
      .collect(Collectors.toList());

    System.out.println(System.currentTimeMillis() - start);
    assertEquals(500, nums.size());
  }

  public void ex17() {}
  public void ex18() {}
}