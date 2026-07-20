public class PalindromeA2 {
    public boolean isPalindrome(String s) {
        int left = 0;
        int right = s.length() - 1;
        while (left < right) {
            char l = Character.toLowerCase(s.charAt(left));
            char r = Character.toLowerCase(s.charAt(right));
            if (!Character.isLetterOrDigit(l)) {
                left++;
            } else if (!Character.isLetterOrDigit(r)) {
                right--;
            } else if (!Character.toString(l).equals(Character.toString(r))) {
                return false;
            } else {
                left++;
                right--;
            }
        }
        return true;
    }
}
