    const deleteAccountBtn = document.getElementById("deleteAccountBtn");
    const confirmationDialog = document.getElementById("confirmationDialog");
    const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
    const cancelDeleteBtn = document.getElementById("cancelDeleteBtn");

    deleteAccountBtn.addEventListener("click", (event) => {
        event.preventDefault();
        confirmationDialog.style.display = "block";
    });

    confirmDeleteBtn.addEventListener("click", () => {

        fetch("/delete_account", {
            method: "POST",
        });

        confirmationDialog.style.display = "none";
    });

    cancelDeleteBtn.addEventListener("click", () => {
        confirmationDialog.style.display = "none";
    });
