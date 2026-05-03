public class PalindromeC3 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder();
        s.chars()
                .filter(Character::isLetterOrDigit)
                .map(Character::toLowerCase)
                .forEach(c -> sb.append((char) c));
        return sb.toString().contentEquals(sb.reverse());
    }
}
