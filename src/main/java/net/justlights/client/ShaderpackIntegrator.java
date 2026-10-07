package net.justlights.client;

import com.mojang.logging.LogUtils;
import net.neoforged.fml.loading.FMLPaths;
import org.slf4j.Logger;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

public class ShaderpackIntegrator {
    private static final Logger LOGGER = LogUtils.getLogger();

    private static final Map<Integer, List<String>> COLOR_MAPPINGS = new LinkedHashMap<>();
    private static final List<String> ALL_COLORS = List.of(
            "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
            "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"
    );

    private static final List<String> BLOCK_TEMPLATES = List.of(
            "{c}_lamp:lit=true",
            "{c}_torch",
            "{c}_wall_torch",
            "{c}_lantern",
            "{c}_campfire:lit=true",
            "{c}_floor_light:lit=true",
            "{c}_chandelier",
            "{c}_jack_o_lantern",
            "{c}_underwater_torch",
            "{c}_underwater_wall_torch"
    );

    static {
        COLOR_MAPPINGS.put(10500, List.of("white", "light_gray", "gray"));
        COLOR_MAPPINGS.put(10640, List.of("brown"));
        COLOR_MAPPINGS.put(10902, List.of("red"));
        COLOR_MAPPINGS.put(10904, List.of("orange"));
        COLOR_MAPPINGS.put(10906, List.of("yellow"));
        COLOR_MAPPINGS.put(10908, List.of("lime"));
        COLOR_MAPPINGS.put(10910, List.of("green"));
        COLOR_MAPPINGS.put(10912, List.of("cyan"));
        COLOR_MAPPINGS.put(10914, List.of("light_blue"));
        COLOR_MAPPINGS.put(10916, List.of("blue"));
        COLOR_MAPPINGS.put(10918, List.of("purple", "black"));
        COLOR_MAPPINGS.put(10920, List.of("magenta"));
        COLOR_MAPPINGS.put(10922, List.of("pink"));
    }

    public static void integrateShaderpacks() {
        try {
            Path gameDir = FMLPaths.GAMEDIR.get();
            Path shaderpacksDir = gameDir.resolve("shaderpacks");
            if (!Files.exists(shaderpacksDir) || !Files.isDirectory(shaderpacksDir)) {
                return;
            }

            try (DirectoryStream<Path> stream = Files.newDirectoryStream(shaderpacksDir)) {
                for (Path entry : stream) {
                    String fileName = entry.getFileName().toString();
                    if (fileName.endsWith(".zip") && !fileName.endsWith(".bak")) {
                        patchZipShaderpack(entry);
                    } else if (Files.isDirectory(entry)) {
                        patchDirectoryShaderpack(entry);
                    }
                }
            }
        } catch (Exception e) {
            LOGGER.warn("[JustLights] Notice while checking shaderpacks: {}", e.getMessage());
        }
    }

    private static void patchZipShaderpack(Path zipPath) {
        String fileName = zipPath.getFileName().toString();
        try {
            boolean needsPatch = false;
            try (ZipFile zip = new ZipFile(zipPath.toFile())) {
                ZipEntry entry = zip.getEntry("shaders/block.properties");
                if (entry != null) {
                    try (InputStream is = zip.getInputStream(entry)) {
                        String content = new String(is.readAllBytes(), StandardCharsets.UTF_8);
                        if (!content.contains("justlights:")) {
                            needsPatch = true;
                        }
                    }
                }
                ZipEntry candleEntry = zip.getEntry("shaders/lib/materials/specificMaterials/terrain/candle.glsl");
                if (candleEntry != null) {
                    try (InputStream is = zip.getInputStream(candleEntry)) {
                        String candleContent = new String(is.readAllBytes(), StandardCharsets.UTF_8);
                        if (!candleContent.contains("blockResCheck")) {
                            needsPatch = true;
                        }
                    }
                }
            }

            if (!needsPatch) {
                return;
            }

            LOGGER.info("[JustLights] Integrating JustLights block properties into shaderpack: {}", fileName);

            // Create backup if not present
            Path bakPath = zipPath.resolveSibling(fileName + ".bak");
            if (!Files.exists(bakPath)) {
                Files.copy(zipPath, bakPath);
            }

            // Create temporary zip
            Path tempZip = Files.createTempFile("justlights_shader_", ".zip");
            try (ZipFile srcZip = new ZipFile(zipPath.toFile());
                 ZipOutputStream zos = new ZipOutputStream(new BufferedOutputStream(Files.newOutputStream(tempZip)))) {

                Enumeration<? extends ZipEntry> entries = srcZip.entries();
                while (entries.hasMoreElements()) {
                    ZipEntry srcEntry = entries.nextElement();
                    byte[] data;
                    try (InputStream is = srcZip.getInputStream(srcEntry)) {
                        data = is.readAllBytes();
                    }

                    if ("shaders/block.properties".equals(srcEntry.getName())) {
                        String content = new String(data, StandardCharsets.UTF_8);
                        content = patchBlockProperties(content);
                        data = content.getBytes(StandardCharsets.UTF_8);
                    } else if ("shaders/lib/colors/blocklightColors.glsl".equals(srcEntry.getName())) {
                        String content = new String(data, StandardCharsets.UTF_8);
                        content = patchGlslColors(content);
                        data = content.getBytes(StandardCharsets.UTF_8);
                    } else if ("shaders/lib/materials/specificMaterials/terrain/candle.glsl".equals(srcEntry.getName())) {
                        String content = new String(data, StandardCharsets.UTF_8);
                        content = patchCandleGlsl(content);
                        data = content.getBytes(StandardCharsets.UTF_8);
                    } else if ("shaders/lib/materials/materialHandling/terrainIPBR.glsl".equals(srcEntry.getName())) {
                        String content = new String(data, StandardCharsets.UTF_8);
                        content = patchTerrainIpbrGlsl(content);
                        data = content.getBytes(StandardCharsets.UTF_8);
                    }

                    ZipEntry newEntry = new ZipEntry(srcEntry.getName());
                    zos.putNextEntry(newEntry);
                    zos.write(data);
                    zos.closeEntry();
                }
            }

            // Replace or in-place overwrite if locked on Windows
            try {
                Files.move(tempZip, zipPath, StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException moveEx) {
                try (java.nio.channels.FileChannel src = java.nio.channels.FileChannel.open(tempZip, StandardOpenOption.READ);
                     java.nio.channels.FileChannel dst = java.nio.channels.FileChannel.open(zipPath, StandardOpenOption.WRITE)) {
                    dst.position(0);
                    dst.transferFrom(src, 0, src.size());
                    dst.truncate(src.size());
                }
                Files.deleteIfExists(tempZip);
            }
            ensureShaderConfig(zipPath);
            LOGGER.info("[JustLights] Successfully integrated colored lighting into: {}", fileName);

        } catch (Exception e) {
            LOGGER.warn("[JustLights] Could not auto-integrate {}: {}", fileName, e.getMessage());
        }
    }

    private static void patchDirectoryShaderpack(Path dirPath) {
        Path bpPath = dirPath.resolve("shaders/block.properties");
        if (!Files.exists(bpPath)) return;

        try {
            String content = Files.readString(bpPath, StandardCharsets.UTF_8);
            if (content.contains("justlights:")) return;

            LOGGER.info("[JustLights] Integrating JustLights into directory shaderpack: {}", dirPath.getFileName());
            String patched = patchBlockProperties(content);
            Files.writeString(bpPath, patched, StandardCharsets.UTF_8);

            Path glslPath = dirPath.resolve("shaders/lib/colors/blocklightColors.glsl");
            if (Files.exists(glslPath)) {
                String glsl = Files.readString(glslPath, StandardCharsets.UTF_8);
                glsl = patchGlslColors(glsl);
                Files.writeString(glslPath, glsl, StandardCharsets.UTF_8);
            }

            Path candlePath = dirPath.resolve("shaders/lib/materials/specificMaterials/terrain/candle.glsl");
            if (Files.exists(candlePath)) {
                String candleGlsl = Files.readString(candlePath, StandardCharsets.UTF_8);
                candleGlsl = patchCandleGlsl(candleGlsl);
                Files.writeString(candlePath, candleGlsl, StandardCharsets.UTF_8);
            }

            Path terrainPath = dirPath.resolve("shaders/lib/materials/materialHandling/terrainIPBR.glsl");
            if (Files.exists(terrainPath)) {
                String terrainGlsl = Files.readString(terrainPath, StandardCharsets.UTF_8);
                terrainGlsl = patchTerrainIpbrGlsl(terrainGlsl);
                Files.writeString(terrainPath, terrainGlsl, StandardCharsets.UTF_8);
            }

            ensureShaderConfig(dirPath);
            LOGGER.info("[JustLights] Successfully integrated into: {}", dirPath.getFileName());
        } catch (Exception e) {
            LOGGER.warn("[JustLights] Could not auto-integrate directory {}: {}", dirPath.getFileName(), e.getMessage());
        }
    }

    private static String patchCandleGlsl(String content) {
        if (content.contains("blockResCheck")) return content;
        String oldWick = "noSmoothLighting = true;\n\ncolor.rgb *= 1.0 + 0.7 * pow2(max(-signMidCoordPos.y + 0.6, float(NdotU > 0.9) * 1.6));";
        String oldWickCrLf = "noSmoothLighting = true;\r\n\r\ncolor.rgb *= 1.0 + 0.7 * pow2(max(-signMidCoordPos.y + 0.6, float(NdotU > 0.9) * 1.6));";
        String newWick = "float blockResCheck = absMidCoordPos.x * atlasSize.x;\n" +
                "if (blockResCheck < 3.0) {\n" +
                "    noSmoothLighting = true;\n\n" +
                "    color.rgb *= 1.0 + 0.7 * pow2(max(-signMidCoordPos.y + 0.6, float(NdotU > 0.9) * 1.6));\n" +
                "} else {\n" +
                "    noDirectionalShading = true;\n" +
                "    lmCoordM.x = 1.0;\n" +
                "}";
        if (content.contains(oldWickCrLf)) {
            content = content.replace(oldWickCrLf, newWick);
        } else if (content.contains(oldWick)) {
            content = content.replace(oldWick, newWick);
        } else if (content.contains("color.rgb *= 1.0 + 0.7 * pow2")) {
            content = content.replace("noSmoothLighting = true;", "float blockResCheck = absMidCoordPos.x * atlasSize.x;\nif (blockResCheck < 3.0) {\n    noSmoothLighting = true;");
            content = content.replace("color.rgb *= 1.0 + 0.7 * pow2(max(-signMidCoordPos.y + 0.6, float(NdotU > 0.9) * 1.6));",
                    "    color.rgb *= 1.0 + 0.7 * pow2(max(-signMidCoordPos.y + 0.6, float(NdotU > 0.9) * 1.6));\n} else {\n    noDirectionalShading = true;\n    lmCoordM.x = 1.0;\n}");
        }
        return content;
    }

    private static String patchTerrainIpbrGlsl(String content) {
        content = content.replace("noSmoothLighting = true;\r\n                                        lmCoordM.x = 0.92;",
                "if (absMidCoordPos.x * atlasSize.x < 3.0) noSmoothLighting = true;\r\n                                        lmCoordM.x = 0.92;");
        content = content.replace("noSmoothLighting = true;\n                                        lmCoordM.x = 0.92;",
                "if (absMidCoordPos.x * atlasSize.x < 3.0) noSmoothLighting = true;\n                                        lmCoordM.x = 0.92;");
        return content;
    }

    private static String patchGlslColors(String content) {
        content = content.replace("float candleColorMult = 2.0;", "float candleColorMult = 7.0;");
        content = content.replace("float candleColorMult = 4.0;", "float candleColorMult = 7.0;");
        content = content.replace("vec3(1.0, 0.1, 0.1)", "vec3(1.3, 0.0, 0.0)"); // Red
        content = content.replace("vec3(1.0, 0.4, 0.1)", "vec3(1.3, 0.35, 0.0)"); // Orange
        content = content.replace("vec3(1.0, 1.0, 0.1)", "vec3(1.2, 1.2, 0.0)"); // Yellow
        content = content.replace("vec3(0.1, 1.0, 0.1)", "vec3(0.0, 1.5, 0.0)"); // Lime
        content = content.replace("vec3(0.3, 1.0, 0.3)", "vec3(0.0, 1.4, 0.1)"); // Green
        content = content.replace("vec3(0.3, 0.8, 1.0)", "vec3(0.0, 1.1, 1.4)"); // Cyan
        content = content.replace("vec3(0.5, 0.65, 1.0)", "vec3(0.1, 0.7, 1.4)"); // Light Blue
        content = content.replace("vec3(0.1, 0.15, 1.0)", "vec3(0.0, 0.1, 1.5)"); // Blue
        content = content.replace("vec3(0.7, 0.3, 1.0)", "vec3(0.9, 0.0, 1.4)"); // Purple
        content = content.replace("vec3(1.0, 0.1, 1.0)", "vec3(1.4, 0.0, 1.2)"); // Magenta
        content = content.replace("vec3(1.0, 0.4, 1.0)", "vec3(1.4, 0.2, 0.9)"); // Pink
        return content;
    }

    private static String patchBlockProperties(String original) {
        StringBuilder sb = new StringBuilder();
        String[] lines = original.split("\r?\n");

        for (String line : lines) {
            boolean matched = false;
            for (Map.Entry<Integer, List<String>> entry : COLOR_MAPPINGS.entrySet()) {
                String prefix = "block." + entry.getKey() + "=";
                if (line.startsWith(prefix)) {
                    List<String> extra = new ArrayList<>();
                    for (String color : entry.getValue()) {
                        for (String template : BLOCK_TEMPLATES) {
                            extra.add("justlights:" + template.replace("{c}", color));
                        }
                    }
                    line = line + " " + String.join(" ", extra);
                    matched = true;
                    break;
                }
            }

            if (!matched && line.startsWith("block.10636=redstone_lamp:lit=false")) {
                List<String> extra = new ArrayList<>();
                for (String color : ALL_COLORS) {
                    extra.add("justlights:" + color + "_lamp:lit=false");
                    extra.add("justlights:" + color + "_campfire:lit=false");
                    extra.add("justlights:" + color + "_floor_light:lit=false");
                }
                line = line + " " + String.join(" ", extra);
            }

            sb.append(line).append("\n");
        }

        return sb.toString();
    }

    private static void ensureShaderConfig(Path shaderPath) {
        try {
            String configName = shaderPath.getFileName().toString() + ".txt";
            Path configPath = shaderPath.resolveSibling(configName);

            Map<String, String> properties = new LinkedHashMap<>();
            if (Files.exists(configPath)) {
                for (String line : Files.readAllLines(configPath, StandardCharsets.UTF_8)) {
                    line = line.trim();
                    if (!line.isEmpty() && !line.startsWith("#") && line.contains("=")) {
                        String[] parts = line.split("=", 2);
                        properties.put(parts[0].trim(), parts[1].trim());
                    }
                }
            }

            // Ensure intensely colored lighting, high saturation, and atmospheric fog are enabled
            properties.put("COLORED_CANDLE_LIGHT", "true");
            properties.put("COLORED_LIGHT_SATURATION", "125");
            properties.put("COLORED_LIGHT_FOG", "true");
            properties.put("COLORED_LIGHT_FOG_I", "1.50");
            if (!properties.containsKey("COLORED_LIGHTING") || "0".equals(properties.get("COLORED_LIGHTING"))) {
                properties.put("COLORED_LIGHTING", "512");
            }

            StringBuilder sb = new StringBuilder();
            sb.append("# JustLights Auto-Configured Settings\n");
            for (Map.Entry<String, String> e : properties.entrySet()) {
                sb.append(e.getKey()).append("=").append(e.getValue()).append("\n");
            }

            Files.writeString(configPath, sb.toString(), StandardCharsets.UTF_8);
        } catch (Exception ignored) {
        }
    }
}
