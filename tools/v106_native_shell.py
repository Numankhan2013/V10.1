from pathlib import Path
import re

p = Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
s = p.read_text(encoding='utf-8')

marker = '// V10.6_NATIVE_SHELL'
if marker not in s:
    # The PDF-renderer build step intentionally replaces MainActivity.java before
    # this installer runs, so never key the shell on a particular PDF helper name.
    required = [
        'import android.view.Window;',
        'private WebView webView;',
        'setContentView(webView)',
        'webView.loadUrl("file:///android_asset/index.html")',
    ]
    for token in required:
        if token not in s:
            raise SystemExit(f'V10.6 installer cannot find required anchor: {token}')

    # Add native UI imports once.
    s = s.replace(
        'import android.view.Window;',
        'import android.view.Window;\nimport android.view.Gravity;\nimport android.view.View;\nimport android.view.ViewGroup;\nimport android.widget.FrameLayout;\nimport android.widget.ImageView;\nimport android.widget.LinearLayout;\nimport android.widget.TextView;',
        1,
    )
    s = s.replace('private WebView webView;', 'private WebView webView;\n    private LinearLayout nativeNav;', 1)

    # Replace the actual WebView-only content view regardless of whitespace/newline style.
    view_pattern = re.compile(
        r'(?m)^(\s*)setContentView\(webView\);\s*webView\.loadUrl\("file:///android_asset/index\.html"\);'
    )
    match = view_pattern.search(s)
    if not match:
        raise SystemExit('V10.6 installer cannot locate WebView content-view/loadUrl block')
    indent = match.group(1)
    replacement = f'''{indent}FrameLayout shell = new FrameLayout(this);\n{indent}shell.setBackgroundColor(Color.rgb(246,248,252));\n{indent}shell.addView(webView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));\n{indent}nativeNav = buildNativeNavigation();\n{indent}FrameLayout.LayoutParams navLp = new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(76));\n{indent}navLp.gravity = Gravity.BOTTOM;\n{indent}navLp.leftMargin = dp(10); navLp.rightMargin = dp(10); navLp.bottomMargin = dp(8);\n{indent}shell.addView(nativeNav, navLp);\n{indent}setContentView(shell);\n{indent}webView.loadUrl("file:///android_asset/index.html");'''
    s = s[:match.start()] + replacement + s[match.end():]

    # Insert shell helpers immediately before the final class closing brace.
    helper = '''\n    private int dp(int v){ return Math.round(v*getResources().getDisplayMetrics().density); }\n    private LinearLayout buildNativeNavigation(){\n        LinearLayout bar=new LinearLayout(this);\n        bar.setOrientation(LinearLayout.HORIZONTAL);\n        bar.setGravity(Gravity.CENTER);\n        bar.setPadding(dp(8),dp(7),dp(8),dp(7));\n        android.graphics.drawable.GradientDrawable bg=new android.graphics.drawable.GradientDrawable();\n        bg.setColor(Color.argb(244,255,255,255));\n        bg.setCornerRadius(dp(24));\n        bg.setStroke(dp(1),Color.rgb(225,229,238));\n        bar.setBackground(bg); bar.setElevation(dp(12));\n        addNavItem(bar,"Home",com.qbank.biochemistry.R.drawable.ic_home_v106,new Runnable(){public void run(){go("dashboard");}});\n        addNavItem(bar,"Practice",com.qbank.biochemistry.R.drawable.ic_practice_v106,new Runnable(){public void run(){go("practice");}});\n        addNavItem(bar,"Tests",com.qbank.biochemistry.R.drawable.ic_tests_v106,new Runnable(){public void run(){go("tests");}});\n        addNavItem(bar,"Data",com.qbank.biochemistry.R.drawable.ic_backup_v106,new Runnable(){public void run(){openBackup();}});\n        return bar;\n    }\n    private void addNavItem(LinearLayout bar,String label,int icon,final Runnable action){\n        LinearLayout item=new LinearLayout(this);\n        item.setOrientation(LinearLayout.VERTICAL); item.setGravity(Gravity.CENTER);\n        item.setPadding(dp(6),dp(2),dp(6),dp(2));\n        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.MATCH_PARENT,1f);\n        lp.setMargins(dp(2),0,dp(2),0); bar.addView(item,lp);\n        ImageView iv=new ImageView(this); iv.setImageResource(icon); iv.setAlpha(.86f);\n        item.addView(iv,new LinearLayout.LayoutParams(dp(24),dp(24)));\n        TextView tv=new TextView(this); tv.setText(label); tv.setTextSize(10);\n        tv.setTextColor(Color.rgb(71,84,105)); tv.setGravity(Gravity.CENTER);\n        tv.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);\n        item.addView(tv,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(22)));\n        item.setOnClickListener(new View.OnClickListener(){public void onClick(View v){\n            v.animate().scaleX(.94f).scaleY(.94f).setDuration(70).withEndAction(new Runnable(){public void run(){\n                v.animate().scaleX(1f).scaleY(1f).setDuration(120);\n            }}); action.run();\n        }});\n    }\n    private void go(String page){ if(webView!=null) webView.evaluateJavascript("location.hash='#"+page+"'",null); }\n    private void openBackup(){ if(webView!=null) webView.evaluateJavascript("window.QB&&window.QB.openBackup&&window.QB.openBackup()",null); }\n    // V10.6_NATIVE_SHELL\n'''
    # The class has one final brace; place helpers before it.
    pos = s.rfind('\n}')
    if pos < 0:
        raise SystemExit('V10.6 installer cannot locate MainActivity class closing brace')
    s = s[:pos] + helper + s[pos:]

checks = [
    marker,
    'private LinearLayout nativeNav;',
    'FrameLayout shell = new FrameLayout(this);',
    'buildNativeNavigation()',
    'ic_home_v106', 'ic_practice_v106', 'ic_tests_v106', 'ic_backup_v106',
    'preparePdfs()',
]
for token in checks:
    if token not in s:
        raise SystemExit(f'V10.6 installer verification failed: {token}')

p.write_text(s, encoding='utf-8')
print('V10.6 native Android shell installed and verified against the post-PDF-renderer MainActivity')
