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
								json.append("\"type\":\"").append(esc(item.type())).append("\",");
								json.append("\"quality\":\"").append(esc(item.quality().name())).append("\",");
								json.append("\"stacks\":").append(item.stacks()).append(",");
								json.append("\"maxStacks\":").append(item.maxStacks()).append(",");
								json.append("\"code\":\"").append(esc(item.code())).append("\"");
								json.append("}");

								if (i < items.size() - 1) json.append(",");
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