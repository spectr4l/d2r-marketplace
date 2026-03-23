import java.io.IOException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.ByteBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
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

    private static boolean isSimpleType(Class<?> type) {
        return type.isPrimitive()
                || type == String.class
                || type == Integer.class
                || type == Long.class
                || type == Boolean.class
                || type == Double.class
                || type == Float.class
                || type == Short.class
                || type == Byte.class
                || type == Character.class
                || type.isEnum();
    }

    private static String valueToJson(Object value) {
        if (value == null) return "null";

        if (value instanceof String s) {
            return "\"" + esc(s) + "\"";
        }

        if (value instanceof Number || value instanceof Boolean) {
            return String.valueOf(value);
        }

        if (value.getClass().isEnum()) {
            return "\"" + esc(((Enum<?>) value).name()) + "\"";
        }

        if (value instanceof List<?> list) {
            StringBuilder json = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                Object entry = list.get(i);
                if (entry == null) {
                    json.append("null");
                } else if (isSimpleType(entry.getClass())) {
                    json.append(valueToJson(entry));
                } else {
                    json.append("\"").append(esc(entry.toString())).append("\"");
                }
                if (i < list.size() - 1) json.append(",");
            }
            json.append("]");
            return json.toString();
        }

        return "\"" + esc(value.toString()) + "\"";
    }

    private static String dumpItem(Item item) {
				StringBuilder json = new StringBuilder();
				json.append("{");

				boolean first = true;

				// ===== GETTERS (igual antes) =====
				for (Method m : item.getClass().getMethods()) {
						if (m.getParameterCount() != 0) continue;
						if (!Modifier.isPublic(m.getModifiers())) continue;
						if (m.getDeclaringClass() == Object.class) continue;

						String name = m.getName();
						if (name.equals("hashCode") || name.equals("toString") || name.equals("getClass")) continue;

						try {
								Object value = m.invoke(item);

								if (!first) json.append(",");
								first = false;

								json.append("\"").append(name).append("\":");
								json.append(valueToJson(value));
						} catch (Exception e) {
								if (!first) json.append(",");
								first = false;

								json.append("\"").append(name).append("_error\":\"").append(e.getMessage()).append("\"");
						}
				}

				// ===== CAMPOS PRIVADOS =====
				try {
						var fields = item.getClass().getDeclaredFields();

						for (var f : fields) {
								f.setAccessible(true);

								Object value = f.get(item);

								if (!first) json.append(",");
								first = false;

								json.append("\"field_").append(f.getName()).append("\":");
								json.append(valueToJson(value));
						}
				} catch (Exception e) {
						if (!first) json.append(",");
						json.append("\"fields_error\":\"").append(e.getMessage()).append("\"");
				}

				json.append("}");
				return json.toString();
		}

    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.println("{\"error\":\"Nenhum arquivo foi informado.\"}");
            return;
        }

        boolean debug = args.length > 1 && "--debug".equalsIgnoreCase(args[1]);

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
            json.append("\"debug\":").append(debug).append(",");
            json.append("\"items\":[");

            for (int i = 0; i < items.size(); i++) {
                Item item = items.get(i);

                if (debug) {
                    json.append(dumpItem(item));
                } else {
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
                }

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