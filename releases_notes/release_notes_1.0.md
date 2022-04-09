## Resolved Issues in 1.0

### New features added to 1.0:
<!--List of new features !-->
- Added endpoints that allow retrieve, create and delete recipes.
- Added endpoint that allows retrieve list of ingredients.
- Added endpoints that allow retrieve, create and delete menus.
- Added endpoint that allows retrieve recipes of a user.
- Added "user" and "servings" fields to Recipe entity.
- Added endpoints that allow score a recipe and retrieve scores.
- Added filters "is_lunch" and "discarded_ingredients" to allow make custom menus.
- Added filter "category" to allow retrieve recipes by category.

### Issues solved in 1.0:
<!--List of bugs and errors solved !-->
- Fixed error when adding ingredient that not exists.
- Fixed bug that did not allow "steps" to be a vector.
- Fixed local and production environments in application settings.
- Fixed error that allowed create two menus to the same day.

### List of known issues in 1.0:
<!--List of bugs and errors not solved at the time of the release !-->
