package com.A1675876.dkspringai1;

public class SineWaveExample {
    public static void main(String[] args) {
        for (int degrees = 0; degrees <= 360; degrees += 30) {
            double radians = Math.toRadians(degrees);
            double sineValue = Math.sin(radians);
            System.out.printf("Angle: %3d° | Radians: %.2f | sin(x): %6.3f%n",
                    degrees, radians, sineValue);
        }
    }
}
