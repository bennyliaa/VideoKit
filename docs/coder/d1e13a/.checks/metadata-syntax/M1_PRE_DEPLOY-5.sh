p=$(pm path com.videokit.app.test); case "$p" in package:/data/app/*/base.apk) ;; *) exit 23;; esac; p=${p#package:}; case "$p" in *'
'*) exit 24;; esac; printf '%s\n' "$p"; sha256sum "$p"