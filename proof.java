import java.util.Scanner;

public class proof {
public static void main(String[] args) {
Scanner scanner = new Scanner(System.in);
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
scanner.close();
}}
