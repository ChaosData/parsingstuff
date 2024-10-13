import java.util.*;
import java.nio.file.*;
import java.io.*;

import com.github.javaparser.*;
import com.github.javaparser.ast.expr.*;
import com.github.javaparser.ast.visitor.*;
import com.github.javaparser.ast.*;

class Main {

  static List<String> getFileNames(Path dir, String ext) {
    List<String> paths = new ArrayList<>();
    try(DirectoryStream<Path> stream = Files.newDirectoryStream(dir)) {
      for (Path path : stream) {
        if(path.toFile().isDirectory()) {
          paths.addAll(getFileNames(path, ext));
        } else {
          if (path.toString().endsWith(ext)) {
            paths.add(path.toString());
          }
        }
      }
    } catch(Throwable t) {
      t.printStackTrace();
    }
    return paths;
  }

            /*  str, path */
  static Map<String, String> uniqstrs = new HashMap<>();
            /* path, str  */
  static Map<String, String> runiqstrs = new HashMap<>();

  public static void main(String[] argv) {
    List<String> paths = getFileNames(Paths.get(argv[0]), argv[1]);
    System.out.println("Found: " + paths.size() + " files");

    for (String path : paths) {
      processFile(path);
    }

    uniqstrs.forEach((k, v) -> {
      if (v != null) {
        String lit = runiqstrs.get(v);
        if (lit == null) {
          runiqstrs.put(v, k);
        } else if (k.length() > lit.length()){
          runiqstrs.put(v, k);
        }
      }
    });

    runiqstrs.forEach((k, v) -> {
      System.out.println(k + ": \"" + v + "\"");
    });

  }

  static void processFile(String path) {
    FileInputStream in = null;
    CompilationUnit cu = null;

    try {
      in = new FileInputStream(path);
      cu = JavaParser.parse(in);
    } catch (Throwable t) {
      t.printStackTrace();
      return;
    } finally {
      try {
        in.close();
      } catch (Throwable t) {
        t.printStackTrace();
      }
    }
    new StrLitVisitor(path).visit(cu, null);
  }

  //note: can potentially use Node::getParentNode() to cmp w/ com.github.javaparser.ast.body.ClassOrInterfaceDeclaration
  private static class StrLitVisitor extends VoidVisitorAdapter {

    String path = null;

    public StrLitVisitor(String _path) {
      path = _path;
    }

    @Override
    public void visit(StringLiteralExpr expr, Object arg) {
      String s = expr.getValue();
      if (uniqstrs.containsKey(s)) {
        uniqstrs.put(s, null);
      } else {
        uniqstrs.put(s, path);
      }
    }
  }

}
