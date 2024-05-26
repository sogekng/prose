public class loops
{
    public static void main(String[] args)
    {
        int count = 0;

        while (count < 10) {
            count = count + 1;
        }

        do {
            count = count - 1;
        } while (count > 0);

        System.out.printf("%d", count);
    }
}
