import java.util.Scanner;

public class proof {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
int amount;
amount = scanner.nextInt();
System.out.printf("You chose amount = %d\n", amount);
if (amount > 3) {
System.out.printf("Amount is greater than 3!\n");
} else if (amount < 3) {
System.out.printf("Amount is less than 3!\n");
} else {
System.out.printf("Amount is exactly 3!\n");
}
int i = 0;
while (i < amount) {
System.out.printf("%d\n", i);
i = i + 1;
}
scanner.close();
}}
