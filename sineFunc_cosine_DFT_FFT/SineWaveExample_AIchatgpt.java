package com.A1675876.dkspringai1;

public class SineWaveExample_AIchatgpt {

    /**
     * Converts an angle in degrees to a readable multiple of pi.
     * Examples: 45° -> pi/4, 90° -> pi/2, 135° -> 3pi/4.
     */
    private static String formatPiAngle(int degrees) {
        if (degrees == 0) {
            return "0";
        }

        // The loop uses 45-degree increments, so each angle is a multiple of pi/4.
        int numerator = degrees / 45;
        int denominator = 4;

        // Simplify the fraction.
        while (numerator % 2 == 0 && denominator > 1) {
            numerator /= 2;
            denominator /= 2;
        }

        String piPart = numerator == 1 ? "pi" : numerator + "pi";
        return denominator == 1 ? piPart : piPart + "/" + denominator;
    }

    public static void main(String[] args) {
        System.out.println("Sine values at multiples of pi:");
        System.out.printf("%-8s | %-10s | %-10s | %-8s%n",
                "Degrees", "Pi angle", "Radians", "sin(x)");
        System.out.println("-----------------------------------------------");

        for (int degrees = 0; degrees <= 360; degrees += 45) {
            double radians = Math.toRadians(degrees);
            double sineValue = Math.sin(radians);

            System.out.printf("%-8d | %-10s | %-10.4f | %8.4f%n",
                    degrees, formatPiAngle(degrees), radians, sineValue);
        }
    }
}
