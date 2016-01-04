Title: Converting Between Long and Wide Formats in R
Date: 2015-12-14 16:27
Modified: 2015-12-14 16:27
Category: R
Tags: tidyr, long, wide, data manipulation
Author: Aleksandr Sinayev
Summary: I show some necessary checks for converting from the long format to the wide format and I comment on which methods I think are best and which format I think is best.

Many applications require dealing with grouped observations. However, there are multiple ways of representing this type of data, namely long and wide. Multiple methods in R offer to convert a dataset from the wide to the long format and vice-versa. In this post, I show some necessary checks for converting from one format to another and I comment on which methods I think are best and which format I think is best.

The main difference is that in the **wide** format, you have one row per group but you have multiple columns, representing the multiple observations.  In the **long** format, you have one row per observation and an additional variable that indicates what group the observation belongs to.

For example, take the `InstEval` dataset in the `lme4` package in `R`. According to the documentation, it is 

>A data frame with 73421 observations on the following 7 variables.

>`s` a factor with levels 1:2972 denoting individual students.

>`d` a factor with 1128 levels from 1:2160, denoting individual professors or lecturers.

>`studage` an ordered factor with ... 

>`lectage` an ordered factor with ... how many semesters back the lecture rated had taken place.

>`service` a binary factor ...

>`dept` a factor with 14 levels, using a random code for the department of the lecture.

>`y` a numeric vector of ratings of lectures by the students, using the discrete scale
1:5, with meanings of ‘poor’ to ‘very good’.

>Each observation is one student’s rating for a specific lecture (of one lecturer, during one semester in the past).

This dataset is in the long format, with one row per observation. In this post, we are going to think of the observations as grouped by professor -- the `d` variable (though we could alternatively think about student as the grouping variable). The present (long) format is great for fitting `lmer` models, like the ones discussed in the `lmer` documentation (or, see Douglas Bates' excellent [book](http://lme4.r-forge.r-project.org/lMMwR/lrgprt.pdf)).
```R
require(lme4)
m1 = lmer(y ~ 1 + (1|s) + (1|d) + (1|dept:service), InstEval)
```
# Going Long to Wide
We might be interested in fitting PCA or factor analysis models. For example, we might want to see if student ratings of professors are essentially similar to each other (represent one component). To check this, we would need to have a dataset with professors as rows and students as columns. That is, student j's rating of professor i would be in the (i,j) entry of the dataset.

## Checking Assumptions
We should make sure our dataset is suitable for the wide format. There are two important checks. First, if a specific student rated a specific professor more than once, this would not be sensible (we would need to fit multiple entries in each cell). We can crosstabulate the data to check whether any student rated any professor more than once.

```
> crosstab = with(InstEval, xtabs(~s + d))
> all(crosstab > 1 == F)
[1] TRUE
```

Fortunately, the answer appears to be no, so it would be sensible to represent the data differently, with one professor representing each row and with the students representing the columns. 

We might also want to see what proportion of students rated each professor.
```
> mean(crosstab==0)
[1] 0.9780991
```
This result indicates that on average, professors were rated by only 2.2 percent of students, meaning that our professor by student matrix is going to be mostly sparse. Using the wide format is more effective when the matrix is less sparse.

Second, we need to get rid of any covariates that are not relevant to a specific professor because we are treating professors as the group. In this case, the third variable (student age) is on the student level and the fourth variable (lecture age) is on the lecture level level, so they need to be deleted.

```
> myeval = InstEval[-(3:4)]
```

There are a few methods we can use to accomplish the task. One of the most commonly recommended is `reshape` in the base installation. However, as you can see below, `reshape` is not very fast, and the command is not very intuitive.

```
> system.time(w <- reshape(myeval,
+   timevar = "s",
+   idvar = c("d","service", "dept"),
+   direction = "wide"))
   user  system elapsed
 41.762   3.923  45.719
```
 
I prefer the faster and more elegant `spread` function in the `tidyr` package. Other alternatives exist including the `reshape2` package, and `unstack` in the base package.
 
```
> require(tidyr)
> system.time(evalwide <- spread(myeval, s, y))
   user  system elapsed
  1.888   0.261   2.168
> head(names(evalwide))
[1] "d"       "service" "dept"    "1"       "2"       "3"
```
 Note that `evalwide` has columns for our professor level covariates and then a list of columns, each labeled with the appropriate student ID. Also note that unlike `reshape`, `spread` is clever enough to figure out that `d`, `service`, and `dept` are professor level variables.
 
 Now, we can do our PCA or factor analysis, or whatever other multivariate analysis our heart desires.
 
# Going Wide to Long
 
 Now imagine we got the dataset in the wide format in the first place and we wanted to model it using `lmer` or get summaries using `aggregate` or do something else that requires the long format. There are no necessary checks this time. Any dataset that can be represented in the wide format can also be represented in the long format.
 
 Again, there are a few methods that are available, but I prefer `gather_` in the `tidyr` package. The first argument is the name of the package, the second is the what you want to call the grouping variable in the new dataset, the third is what you want to call the measurement variable in the new dataset, and then the columns in the old, wide dataset that need to be converted.
 
```
newlong = gather_(evalwide, 's', 'y', '1':'2972')
lmer(y~(1+service|s), newlong)
```
 
 Our dataset is ready for `lmer` type models again!
 
*Technical note: This version of the gather package takes string names of the variables. Alternatively, `gather` would take the actual names (wouldn't use quotes). In this case that's not appropriate because 1:2972 would evaluate to a sequence of numbers, not variable names.*

# Concluding Remarks
The wide format is better for storage in cases where it is not sparse, and in cases a lot of the data is on the level of that group. However, I generally recommend the long format if the size of the dataset is not an issue. This is because the long format can always accomodate the information available in a wide format, but it can also accomodate data in which the observations can be grouped in multiple (more than two) ways and data that includes covariates on more than one group.