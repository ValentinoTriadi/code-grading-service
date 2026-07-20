public class PalindromeC1 {
    public boolean isPalindrome(String s) {
        StringBuilder sb = new StringBuilder(s.toLowerCase());
        StringBuilder rev = new StringBuilder(sb).reverse();
        return sb.toString().equals(rev.toString());
    }
}
