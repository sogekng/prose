import java.util.Scanner;

public class proof {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
<<<<<<< HEAD
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
=======
int count = 0;
boolean verdadeiro;
String mostrar;
verdadeiro = true;
mostrar = "resultado: ";
do {
count = count + 1;
System.out.println(count);
verdadeiro = false;
} while ((count < 10) && (verdadeiro == true));
>>>>>>> de39643bbb3c2bc43aa2583f98300c9e29f6a14d
scanner.close();
}}
