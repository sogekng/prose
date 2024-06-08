import java.util.Scanner;

public class test {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
int x = 25;
final int Y = 35;
int z;
z = x + Y;
System.out.printf("z = %d\n", z);
final String WELCOME = "Welcome to my program\n";
System.out.printf(WELCOME);
int j;
j = scanner.nextInt();
int i = 0;
while (i < j) {
System.out.printf("i = %d\n", i);
i = i + 1;
}
if (i == j - 1) {
System.out.printf("i reached its maximum\n");
} else if (i > 0) {
System.out.printf("i did not progress\n");
} else {
System.out.printf("i decreased somehow\n");
}
do {
System.out.printf("Testing!\n");
} while (false);
scanner.close();
}}
