import { createTheme } from "@mantine/core";

export const mantineTheme = createTheme({
  primaryColor: "teal",
  defaultRadius: "lg",
  fontFamily: "var(--font-body)",
  headings: {
    fontFamily: "var(--font-heading)",
    fontWeight: "700"
  },
  colors: {
    teal: [
      "#e6f7f4",
      "#cff1ec",
      "#9fe1d7",
      "#6bcfbe",
      "#42bca8",
      "#2aa28f",
      "#1f8b85",
      "#1a6f6d",
      "#17595b",
      "#123f41"
    ]
  },
  components: {
    Card: {
      defaultProps: {
        radius: "xl",
        padding: "lg",
        shadow: "sm",
        withBorder: true
      }
    },
    Button: {
      defaultProps: {
        radius: "xl"
      }
    },
    TextInput: {
      defaultProps: {
        radius: "md"
      }
    },
    Select: {
      defaultProps: {
        radius: "md"
      }
    },
    Modal: {
      defaultProps: {
        radius: "xl",
        centered: true,
        overlayProps: { backgroundOpacity: 0.45, blur: 10 }
      }
    },
    Drawer: {
      defaultProps: {
        radius: "xl",
        overlayProps: { backgroundOpacity: 0.35, blur: 8 }
      }
    }
  }
});
