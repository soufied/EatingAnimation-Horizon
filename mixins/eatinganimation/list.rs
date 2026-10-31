fn official_eatinganimation_listed(mods: &mut Vec<crate::game::native_hooks::NativeMod>) {
    mods.push(crate::game::native_hooks::NativeMod {
        id: "eatinganimation".into(),
        title: "Eating Animation 0.1.1".into(),
        description:
            "Bitten frames for the food and potion in your hand while you eat or drink it.".into(),
        keys: Vec::new(),
    });
}
