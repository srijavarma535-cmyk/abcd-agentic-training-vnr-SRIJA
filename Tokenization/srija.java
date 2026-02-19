public class srija {
    public static void main(String[] args) {

        String text = "Java is easy to learn";

        // Tokenize using space
        String[] tokens = text.split(" ");

        System.out.println("Tokens:");
        for (String token : tokens) {
            System.out.println(token);
        }
    }
}
