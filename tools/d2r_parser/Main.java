import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import io.github.paladijn.d2rsavegameparser.model.D2Character;
import io.github.paladijn.d2rsavegameparser.model.Item;
import io.github.paladijn.d2rsavegameparser.model.SharedStashTab;
import io.github.paladijn.d2rsavegameparser.parser.CharacterParser;
import io.github.paladijn.d2rsavegameparser.parser.SharedStashParser;

public class Main {
    private static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\r", "")
                .replace("\n", "\\n");
    }

    private static String stringListToJson(List<?> list) {
        if (list == null) return "[]";

        StringBuilder json = new StringBuilder("[");
        for (int i = 0; i < list.size(); i++) {
            Object value = list.get(i);
            json.append("\"").append(esc(String.valueOf(value))).append("\"");
            if (i < list.size() - 1) json.append(",");
        }
        json.append("]");
        return json.toString();
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("{\"error\":\"Nenhum arquivo foi informado.\"}");
            return;
        }

        try {
            Path filePath = Path.of(args[0]);
            byte[] bytes = Files.readAllBytes(filePath);
            ByteBuffer buffer = ByteBuffer.wrap(bytes);

            String lower = filePath.getFileName().toString().toLowerCase();
            List<Item> items = new ArrayList<>();
            String sourceName = filePath.getFileName().toString();

            if (lower.endsWith(".d2s")) {
                CharacterParser parser = new CharacterParser(false);
                D2Character character = parser.parse(buffer);
                items = character.items();
                sourceName = character.name();
            } else if (lower.endsWith(".d2i")) {
                SharedStashParser parser = new SharedStashParser(false);
                List<SharedStashTab> tabs = parser.parse(buffer);
                for (SharedStashTab tab : tabs) {
                    items.addAll(tab.items());
                }
            } else {
                System.out.println("{\"error\":\"Formato não suportado.\"}");
                return;
            }

            StringBuilder json = new StringBuilder();
            json.append("{");
            json.append("\"source\":\"").append(esc(sourceName)).append("\",");
            json.append("\"items\":[");

            for (int i = 0; i < items.size(); i++) {
                Item item = items.get(i);
                String name = item.itemName();
                if (name == null || name.isBlank()) {
                    name = item.type();
                }

                json.append("{");
                json.append("\"name\":\"").append(esc(name)).append("\",");
                json.append("\"itemName\":\"").append(esc(item.itemName())).append("\",");
                json.append("\"type\":\"").append(esc(item.type())).append("\",");
                json.append("\"itemType\":\"").append(esc(item.itemType().name())).append("\",");
                json.append("\"quality\":\"").append(esc(item.quality().name())).append("\",");
                json.append("\"stacks\":").append(item.stacks()).append(",");
                json.append("\"maxStacks\":").append(item.maxStacks()).append(",");
                json.append("\"code\":\"").append(esc(item.code())).append("\",");
                json.append("\"baseDefense\":").append(item.baseDefense()).append(",");
                json.append("\"durability\":").append(item.durability()).append(",");
                json.append("\"maxDurability\":").append(item.maxDurability()).append(",");
                json.append("\"reqStr\":").append(item.reqStr()).append(",");
                json.append("\"reqDex\":").append(item.reqDex()).append(",");
                json.append("\"reqLvl\":").append(item.reqLvl()).append(",");
                json.append("\"cntSockets\":").append(item.cntSockets()).append(",");
                json.append("\"cntFilledSockets\":").append(item.cntFilledSockets()).append(",");
                json.append("\"isEthereal\":").append(item.isEthereal()).append(",");
                json.append("\"isRuneword\":").append(item.isRuneword()).append(",");
                json.append("\"isIdentified\":").append(item.isIdentified()).append(",");
                json.append("\"invWidth\":").append(item.invWidth()).append(",");
                json.append("\"invHeight\":").append(item.invHeight()).append(",");
                json.append("\"x\":").append(item.x()).append(",");
                json.append("\"y\":").append(item.y()).append(",");
                json.append("\"properties\":").append(stringListToJson(item.properties())).append(",");
                json.append("\"socketedItems\":").append(stringListToJson(item.socketedItems()));
                json.append("}");

                if (i < items.size() - 1) json.append(",");
            }

            json.append("]}");
            System.out.println(json);
        } catch (IOException e) {
            System.out.println("{\"error\":\"Erro ao ler arquivo: " + esc(e.toString()) + "\"}");
        } catch (Exception e) {
            String error = e.toString();

            if (error.contains("IndexOutOfBoundsException")) {
                System.out.println("{\"error\":\"MODDED_ITEMS_DETECTED\"}");
            } else {
                System.out.println("{\"error\":\"" + esc(error) + "\"}");
            }
        }
    }
}