import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;

public class BstD2 {
    private final TreeMap<Integer, Boolean> map = new TreeMap<>();

    public void insert(int key) {
        map.putIfAbsent(key, Boolean.TRUE);
    }

    public boolean contains(int key) {
        return map.containsKey(key);
    }

    public boolean delete(int key) {
        return map.remove(key) != null;
    }

    public List<Integer> inorder() {
        return new ArrayList<>(map.keySet());
    }

    public int size() {
        return map.size();
    }
}
