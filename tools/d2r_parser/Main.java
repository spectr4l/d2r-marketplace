import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import io.github.paladijn.d2rsavegameparser.model.D2Character;
import io.github.paladijn.d2rsavegameparser.model.Item;
import io.github.paladijn.d2rsavegameparser.parser.CharacterParser;

public class Main {

    private static String esc(String s) {
        if (s == null) return "";
        return s
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "")
            .replace("\n", "\\n");
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("{\"error\":\"Nenhum arquivo foi informado.\"}");
            return;
        }

        try {
            Path savePath = Path.of(args[0]);

            if (args.length > 1) {
                System.setProperty("excelPath", args[1]);
            }

            byte[] bytes = Files.readAllBytes(savePath);
            ByteBuffer buffer = ByteBuffer.wrap(bytes);

            CharacterParser parser = new CharacterParser(false);
            D2Character character = parser.parse(buffer);

            List<Item> items = character.items();

            StringBuilder json = new StringBuilder();
            json.append("{");
            json.append("\"character_name\":\"").append(esc(character.name())).append("\",");
            json.append("\"items\":[");

            for (int i = 0; i < items.size(); i++) {
                Item item = items.get(i);

                String name = item.itemName();
                if (name == null || name.isBlank()) {
                    name = item.type();
                }

                json.append("{");
                json.append("\"name\":\"").append(esc(name)).append("\",");
                json.append("\"type\":\"").append(esc(item.type())).append("\",");
                json.append("\"quality\":\"").append(esc(item.quality().name())).append("\"");
                json.append("}");

                if (i < items.size() - 1) {
                    json.append(",");
                }
            }

            json.append("]}");
            System.out.println(json);

        } catch (IOException e) {
            System.out.println("{\"error\":\"Erro ao ler arquivo: " + esc(e.toString()) + "\"}");
        } catch (Exception e) {
            System.out.println("{\"error\":\"" + esc(e.toString()) + "\"}");
        }
    }
}