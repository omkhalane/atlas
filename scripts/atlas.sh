check_and_update_chrome() {

    echo ""
    echo "Checking Chrome version..."
    echo ""

    if ! command -v google-chrome >/dev/null 2>&1; then
        echo "❌ Google Chrome is not installed."
        return 1
    fi

    CURRENT_VERSION="$(
        google-chrome --version |
        grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' |
        head -1
    )"

    echo "Installed Chrome:"
    echo "  $CURRENT_VERSION"

    MAJOR_VERSION="$(
        echo "$CURRENT_VERSION" |
        cut -d. -f1
    )"

    echo ""

    # Chrome 144 is required for Atlas's
    # automatic existing-session connection.
    if [ "$MAJOR_VERSION" -lt 144 ]; then

        echo "⚠️ Chrome $MAJOR_VERSION is too old."
        echo "Atlas requires Chrome 144+."
        echo ""

        read -rp \
            "Update Chrome now? [Y/n]: " \
            ANSWER

        ANSWER="${ANSWER:-Y}"

        if [[ "$ANSWER" =~ ^[Yy]$ ]]; then

            echo ""
            echo "Updating Chrome..."
            echo ""

            sudo apt-get update

            sudo apt-get \
                --only-upgrade \
                install \
                google-chrome-stable

            if [ "$?" -ne 0 ]; then

                echo ""
                echo "❌ Chrome update failed."
                return 1

            fi

        else

            echo ""
            echo "❌ Chrome 144+ is required for AutoConnect."
            return 1

        fi

    else

        echo "✓ Chrome version supports AutoConnect."

    fi
}