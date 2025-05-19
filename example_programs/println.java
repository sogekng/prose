import java.util.Scanner;

public class exemplo {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
System.out.println("%d == 2", (1+1));
System.out.println("%d == 0", (1-1));
System.out.println("%d == 1", (1*1));
System.out.println("%d == 5", (10/2));
System.out.println("%d == 7", (5+1*2));
System.out.println("%d == 4", (5/2+1*2));
System.out.println("%d == 8", (5/2+1*2*3));
System.out.println("%d == 7", (2/2+1*2*3));
System.out.println("%d == 0", (2/(2+1)*2*3));
scanner.close();
}}
