# Eating Animation (Horizon native mod)

![Eating Animation icon](icons/eatinganimation.png)

**Port of Eating Animation for Horizon.** Based on [Eating Animation](https://github.com/Theoness1/EatingAnimation) by Theoness1.

![Eating animation preview](icons/eatinganimation.gif)

## What it does

While you eat food, or drink a potion or milk, the item in your hand shows its bitten frames as you go.

The frames come from a resource pack. You can use one of two options:

- **Ready-made pack**, included in Releases:
  - `EatingAnimationVanillaTexturePack.zip`
  
  Put the one you want into Horizon's `resourcepacks/` folder.
- **Build your own** from your copy of the EatingAnimation download, with `tools/make_frame_pack.py`:

  ```sh
  python3 tools/make_frame_pack.py <EatingAnimation download (zip or folder)> <out.zip>
  ```

  Then drop the resulting zip into Horizon's `resourcepacks/` folder.

## Build

```sh
horizon-launcher native-build . --trust-native-code
```

## Credits

- Eating Animation by [Theoness1](https://github.com/Theoness1/EatingAnimation).

## License

MIT. See [LICENSE](LICENSE).