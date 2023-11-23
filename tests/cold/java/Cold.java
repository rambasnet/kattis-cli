//  https://open.kattis.com/problems/cold

import java.util.*;
import java.io.*;

public class Cold {

    Scanner in;
    PrintStream out;

    public static void main(String [] args) throws Exception {
        Cold main = new Cold();
        main.in = new Scanner(System.in);
        main.out = System.out;
        main.run();
    }

    void run() {
        read();
        solve();
        write();
    }

    int[] temperatures;

    void read() {
        int n = in.nextInt();
        temperatures = new int[n];
        for (int i = 0; i < n; ++i) {
            temperatures[i] = in.nextInt();
        }
    }

    int negatives;

    void solve() {
        negatives = 0;
        for (int i = 0; i < temperatures.length; ++i) {
            if (temperatures[i] < 0) {
                ++negatives;
            }
        }
    }

    void write() {
        out.println(negatives);
    }

}
