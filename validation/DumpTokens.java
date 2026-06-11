// Dump Quran tokens at requested locations using JQuranTree (the API named in TASK.txt).
// Input: CSV of chapter,verse,word (1-based). Output: chapter,verse,word,letters-only-token.
//
// Build/run (JQuranTree cloned + compiled to CLASSES, resources copied alongside):
//   javac -cp CLASSES -d CLASSES validation/DumpTokens.java
//   java -cp CLASSES DumpTokens locations.csv tokens.csv
import org.jqurantree.orthography.Document;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpTokens {
    public static void main(String[] args) throws Exception {
        try (BufferedReader in = new BufferedReader(new FileReader(args[0]));
             PrintWriter out = new PrintWriter(new FileWriter(args[1]))) {
            String line;
            while ((line = in.readLine()) != null) {
                String[] p = line.trim().split(",");
                int c = Integer.parseInt(p[0]);
                int v = Integer.parseInt(p[1]);
                int w = Integer.parseInt(p[2]);
                // Raw verse text split on spaces; normalization happens on the Python side.
                // (Some Uthmani marks, e.g. the silent-alif U+06DF, break JQuranTree's
                // per-character transforms, so we avoid removeDiacritics/removeNonLetters.)
                String token = "<MISSING>";
                try {
                    String[] tokens = Document.getVerse(c, v).toUnicode().split(" ");
                    if (w >= 1 && w <= tokens.length) {
                        token = tokens[w - 1];
                    }
                } catch (RuntimeException e) {
                    // leave <MISSING>
                }
                out.println(c + "," + v + "," + w + "," + token);
            }
        }
    }
}
