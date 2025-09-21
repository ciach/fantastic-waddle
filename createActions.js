    locator_selectOption: {
      function: async (args: {
        elementId?: string;
        cssSelector?: string;
        value?: string | string[];
        label?: string | string[];
        index?: number | number[];
      }) => {
        const { elementId, cssSelector, value, label, index } = args;

        let locator;

        if (elementId) {
          locator = page.locator(`[data-element-id="${elementId}"]`);
        } else if (cssSelector) {
          locator = page.locator(cssSelector);
        } else {
          throw new Error(
            "You must provide either an elementId or a cssSelector.",
          );
        }

        if (value !== undefined) {
          await locator.selectOption(value);
        } else if (label !== undefined) {
          const options = Array.isArray(label)
            ? label.map((l) => ({ label: l }))
            : { label };
          await locator.selectOption(options);
        } else if (index !== undefined) {
          const options = Array.isArray(index)
            ? index.map((i) => ({ index: i }))
            : { index };
          await locator.selectOption(options);
        } else {
          throw new Error(
            "You must provide at least one of the parameters: value, label, or index.",
          );
        }

        return { success: true };
      },
      name: "locator_selectOption",
      description:
        "Selects option(s) in a <select> element. Requires either an elementId (obtained via locateElement) or a direct cssSelector.",
      parse: (args: string) => {
        return z
          .object({
            elementId: z.string().optional(),
            cssSelector: z.string().optional(),
            value: z.union([z.string(), z.array(z.string())]).optional(),
            label: z.union([z.string(), z.array(z.string())]).optional(),
            index: z.union([z.number(), z.array(z.number())]).optional(),
          })
          .refine(
            (data) =>
              data.elementId !== undefined || data.cssSelector !== undefined,
            {
              message: "Either elementId or cssSelector must be provided.",
            },
          )
          .refine(
            (data) =>
              data.value !== undefined ||
              data.label !== undefined ||
              data.index !== undefined,
            {
              message:
                "At least one of value, label, or index must be provided.",
            },
          )
          .parse(JSON.parse(args));
      },
      parameters: {
        type: "object",
        properties: {
          elementId: {
            type: "string",
            description:
              "The ID of the <select> element, obtained via locateElement.",
          },
          cssSelector: {
            type: "string",
            description:
              "CSS selector to locate the <select> element directly, e.g., '#my-select' or 'form select'.",
          },
          value: {
            type: ["string", "array"],
            description:
              "Select options with matching value attribute. Can be a string or an array for multi-select.",
            items: {
              type: "string"
            }
          },
          label: {
            type: ["string", "array"],
            description:
              "Select options with matching visible text. Can be a string or an array for multi-select.",
            items: {
              type: "string"
            }
          },
          index: {
            type: ["number", "array"],
            description:
              "Select options by their index (zero-based). Can be a number or an array for multi-select.",
            items: {
              type: "number"
            }
          },
        },
      },
    },
    expect_toBe: {
      function: (args: { actual: string; expected: string }) => {
        return {
          actual: args.actual,
          expected: args.expected,
          success: args.actual === args.expected,
        };
      },
      name: "expect_toBe",
      description:
        "Asserts that the actual value is equal to the expected value.",
      parse: (args: string) => {
        return z
          .object({
            actual: z.string(),
            expected: z.string(),
          })
          .parse(JSON.parse(args));
      },
      parameters: {
        type: "object",
        properties: {
          actual: {
            type: "string",
          },
          expected: {
            type: "string",
          },
        },
      },
    },
