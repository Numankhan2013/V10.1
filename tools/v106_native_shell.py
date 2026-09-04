from pathlib import Path

p = Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
s = p.read_text(encoding='utf-8')

# Idempotent but never silently succeeds: either the shell is present, or we install it and verify it.
marker = '// V10.6_NATIVE_SHELL'
if marker not in s:
    required = [
        'import android.view.Window;',
        'private WebView webView;',
        'setContentView(webView);',
        'webView.loadUrl("file:///android_asset/index.html");',
        '    private void preparePhysiologyPdf()',
    ]
    for token in required:
        if token not in s:
            raise SystemExit(f'V10.6 installer cannot find required anchor: {token}')

    s = s.replace(
        'import android.view.Window;',
        'import android.view.Window;\nimport android.view.Gravity;\nimport android.view.View;\nimport android.view.ViewGroup;\nimport android.widget.FrameLayout;\nimport android.widget.ImageView;\nimport android.widget.LinearLayout;\nimport android.widget.TextView;',
        1,
    )
    s = s.replace('private WebView webView;', 'private WebView webView;\n    private LinearLayout nativeNav;', 1)
    s = s.replace(
        'setContentView(webView);\n        webView.loadUrl("file:///android_asset/index.html");',
        '''FrameLayout shell = new FrameLayout(this);
        shell.setBackgroundColor(Color.rgb(246,248,252));
        shell.addView(webView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
        nativeNav = buildNativeNavigation();
        FrameLayout.LayoutParams navLp = new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, dp(76));
        navLp.gravity = Gravity.BOTTOM;
        navLp.leftMargin = dp(10); navLp.rightMargin = dp(10); navLp.bottomMargin = dp(8);
        shell.addView(nativeNav, navLp);
        setContentView(shell);
        webView.loadUrl("file:///android_asset/index.html");''',
        1,
    )
    insert = '''
    private int dp(int v){ return Math.round(v*getResources().getDisplayMetrics().density); }
    private LinearLayout buildNativeNavigation(){
        LinearLayout bar=new LinearLayout(this);
        bar.setOrientation(LinearLayout.HORIZONTAL);
        bar.setGravity(Gravity.CENTER);
        bar.setPadding(dp(8),dp(7),dp(8),dp(7));
        android.graphics.drawable.GradientDrawable bg=new android.graphics.drawable.GradientDrawable();
        bg.setColor(Color.argb(244,255,255,255));
        bg.setCornerRadius(dp(24));
        bg.setStroke(dp(1),Color.rgb(225,229,238));
        bar.setBackground(bg); bar.setElevation(dp(12));
        addNavItem(bar,"Home",com.qbank.biochemistry.R.drawable.ic_home_v106,new Runnable(){public void run(){go("dashboard");}});
        addNavItem(bar,"Practice",com.qbank.biochemistry.R.drawable.ic_practice_v106,new Runnable(){public void run(){go("practice");}});
        addNavItem(bar,"Tests",com.qbank.biochemistry.R.drawable.ic_tests_v106,new Runnable(){public void run(){go("tests");}});
        addNavItem(bar,"Data",com.qbank.biochemistry.R.drawable.ic_backup_v106,new Runnable(){public void run(){openBackup();}});
        return bar;
    }
    private void addNavItem(LinearLayout bar,String label,int icon,final Runnable action){
        LinearLayout item=new LinearLayout(this);
        item.setOrientation(LinearLayout.VERTICAL); item.setGravity(Gravity.CENTER);
        item.setPadding(dp(6),dp(2),dp(6),dp(2));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,ViewGroup.LayoutParams.MATCH_PARENT,1f);
        lp.setMargins(dp(2),0,dp(2),0); bar.addView(item,lp);
        ImageView iv=new ImageView(this); iv.setImageResource(icon); iv.setAlpha(.86f);
        item.addView(iv,new LinearLayout.LayoutParams(dp(24),dp(24)));
        TextView tv=new TextView(this); tv.setText(label); tv.setTextSize(10);
        tv.setTextColor(Color.rgb(71,84,105)); tv.setGravity(Gravity.CENTER);
        tv.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);
        item.addView(tv,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,dp(22)));
        item.setOnClickListener(new View.OnClickListener(){public void onClick(View v){
            v.animate().scaleX(.94f).scaleY(.94f).setDuration(70).withEndAction(new Runnable(){public void run(){
                v.animate().scaleX(1f).scaleY(1f).setDuration(120);
            }}); action.run();
        }});
    }
    private void go(String page){ if(webView!=null) webView.evaluateJavascript("location.hash='#"+page+"'",null); }
    private void openBackup(){ if(webView!=null) webView.evaluateJavascript("window.QB&&window.QB.openBackup&&window.QB.openBackup()",null); }
    // V10.6_NATIVE_SHELL
'''
    s = s.replace('    private void preparePhysiologyPdf()', insert + '\n    private void preparePhysiologyPdf()', 1)

checks = [
    marker,
    'private LinearLayout nativeNav;',
    'FrameLayout shell = new FrameLayout(this);',
    'buildNativeNavigation()',
    'ic_home_v106', 'ic_practice_v106', 'ic_tests_v106', 'ic_backup_v106',
]
for token in checks:
    if token not in s:
        raise SystemExit(f'V10.6 installer verification failed: {token}')

p.write_text(s, encoding='utf-8')
print('V10.6 native Android shell installed and verified')